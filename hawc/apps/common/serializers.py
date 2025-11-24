from collections import defaultdict
from typing import Any

import jsonschema
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel
from pydantic import ValidationError as PydanticError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DrfValidationError
from rest_framework.request import QueryDict
from rest_framework.settings import api_settings
from rest_framework.utils import html
from rest_framework.validators import UniqueTogetherValidator

from .helper import get_id_from_choices


def validate_pydantic[T: BaseModel](pydantic_class: type[T], field: str | None, data: Any) -> T:
    """Validation helper to validate a field to a pydantic model.

    Args:
        pydantic_class (BaseModel): A Pydantic base class
        field (str|None): the field to raise the error on, or None
        data (Any): the data to be validated

    Raises:
        ValidationError: a DRF Validation error

    Returns:
        BaseModel: The pydantic BaseModel
    """
    try:
        return pydantic_class.model_validate(data)
    except PydanticError as err:
        message = {field: err.json()} if field else err.json()
        raise DrfValidationError(message) from err


def validate_jsonschema(data: Any, schema: dict) -> Any:
    """Validate data and return if appropriate; else raise django ValidationError.

    Args:
        data (Any): The data to validate
        schema (dict): The jsonschema to validate against

    Raises:
        serializers.ValidationError: If validation is unsuccessful

    Returns:
        Any: The unmodified, but validated dataset
    """
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as err:
        raise serializers.ValidationError(err.message) from err
    return data


class UnusedSerializer(serializers.Serializer):
    """
    Nondescript serializer. Used in instances where a view does not use a serializer
    but one needs to be set, such as for OpenAPI generation.
    """

    pass


class ExportQuerySerializer(serializers.Serializer):
    """
    Serializer for exports that may or may not include unpublished data.
    """

    unpublished = serializers.BooleanField(default=False)


def get_matching_instance(Model: models.Model, data: dict, field_name: str) -> models.Model:
    """
    Return a matching django model object or throw ValidationError if not found.

    Args:
        model: (models.Model): The model to fetch an instance of
        data (dict): the data dictionary
        field_name (str): the ID field name

    Returns:
        models.Model: A matching model instance
    """
    err = {}
    id_ = data.get(field_name)

    if id_ is None:
        err[field_name] = f"{field_name} is required."
        raise serializers.ValidationError(err)

    try:
        return Model.objects.get(id=id_)
    except ValueError as error:
        err[field_name] = f"`{field_name} must be a number; got {id_}."
        raise serializers.ValidationError(err) from error
    except models.ObjectDoesNotExist as error:
        err[field_name] = f"{Model.__name__} {id_} does not exist."
        raise serializers.ValidationError(err) from error


def get_matching_instances(Model: models.Model, data: dict, field_name: str) -> list[models.Model]:
    """
    Return a matching django models list or throw ValidationError if not found.

    Args:
        model: (models.Model): The model to fetch an instance of
        data (dict): the data dictionary
        field_name (str): the IDs field name

    Returns:
        models.Model: A list of matching model instances
    """
    err = {}
    ids = data.get(field_name)

    if ids is None:
        err[field_name] = f"{field_name} is required."
        raise serializers.ValidationError(err)

    instances = []
    for id_ in ids:
        try:
            instances.append(Model.objects.get(id=id_))
        except ValueError as error:
            err[field_name] = f"`{field_name} must be a number; got {id_}."
            raise serializers.ValidationError(err) from error
        except models.ObjectDoesNotExist as error:
            err[field_name] = f"{Model.__name__} {id_} does not exist."
            raise serializers.ValidationError(err) from error

    return instances


class FlexibleChoiceField(serializers.ChoiceField):
    """
    ChoiceField subclass that accepts either the raw choice value OR a case-insensitive
    display value when supplying data.
    """

    def to_representation(self, obj):
        if obj == "" and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == "" and self.allow_blank:
            return ""

        # Look for an exact match of either key or val
        for key, val in self._choices.items():
            if key == data or val == data:
                return key

        # No exact match; if a string was passed in let's try case-insensitive value match
        if isinstance(data, str):
            key = get_id_from_choices(self._choices.items(), data)
            if key is not None:
                return key

        self.fail("invalid_choice", input=data)


class FlexibleChoiceArrayField(serializers.ChoiceField):
    """
    like FlexibleChoiceField; accepts either the raw choice value OR a case-insensitive
    display value when supplying data, intended for choice fields wrapped in an ArrayField
    """

    # dupe invalid_choice in ChoiceField, and create a new one that we'll use
    default_error_messages = {
        "invalid_choice": _('"{input}" is not a valid choice.'),
        "full_custom": _("{input}"),
    }

    def to_representation(self, obj):
        if len(obj) == 0 and self.allow_blank:
            return obj
        return [self._choices[x] for x in obj]

    def to_internal_value(self, data):
        if (data is None or len(data) == 0) and self.allow_blank:
            return []
        else:
            converted_values = []
            invalid_values = []
            for x in data:
                element_handled = False
                # Look for an exact match of either key or val
                for key, val in self._choices.items():
                    if key == x or val == x:
                        converted_values.append(key)
                        element_handled = True
                        break

                if not element_handled:
                    # No exact match; if a string was passed in let's try case-insensitive value match
                    if isinstance(x, str):
                        key = get_id_from_choices(self._choices.items(), x)
                        if key is not None:
                            converted_values.append(key)
                            element_handled = True

                if not element_handled:
                    invalid_values.append(x)

            if len(invalid_values) == 0:
                return converted_values
            else:
                invalid_summary = ", ".join([f"'{x}'" for x in invalid_values])
                self.fail(
                    "full_custom",
                    input=f"input {data} contained invalid value(s): {invalid_summary}.",
                )


class FlexibleDBLinkedChoiceField(FlexibleChoiceField):
    """
    FlexibleChoiceField subclass which derives its choices from a model/database table and optionally supports multiples.

    Used for instance when:
        * linking an epi group to one or more ethnicities.
        * linking a epi result to a single metric
        * etc.
    """

    default_error_messages = {
        "invalid_choice": _('"{input}" is not a valid choice.'),
        "not_a_list": _('Expected a list of items but got type "{input_type}".'),
    }

    def __init__(
        self,
        mapped_model: models.Model,
        serializer_class: type[serializers.ModelSerializer],
        field_for_descriptor: str,
        many: bool,
    ):
        super().__init__(choices=[])
        self.serializer = serializer_class()
        self.mapped_model = mapped_model
        self.field_for_descriptor = field_for_descriptor
        self.many = many
        self.related_objects_loaded = False

    def load_related_objects_if_needed(self, force_reload=False):
        """
        Internal helper function that loads choices from the database.

        Called when needed by to_representation / to_internal_value if the choices have not already been fetched.

        Args:
            force_reload (bool): force db choices to be re-fetched from the database.
        """
        if self.related_objects_loaded is False or force_reload:
            db_choices = []
            mapped_objects = self.mapped_model.objects.all()

            for mapped_object in mapped_objects:
                loop_id = mapped_object.id
                loop_descriptor = getattr(mapped_object, self.field_for_descriptor)
                db_choices.append((loop_id, loop_descriptor))

            self.choices = db_choices
            self.related_objects_loaded = True

    def to_representation(self, obj):
        self.load_related_objects_if_needed()

        if self.many:
            return [self.serializer.to_representation(el) for el in obj.all()]
        else:
            return self.serializer.to_representation(obj)

    def to_internal_value(self, data):
        self.load_related_objects_if_needed()

        if self.many:
            if isinstance(data, str) or not hasattr(data, "__iter__"):
                self.fail("not_a_list", input_type=type(data).__name__)
            # Arguments for super() needed b/c of scoping inside comprehensions
            resolved_ids = [
                super(FlexibleDBLinkedChoiceField, self).to_internal_value(item) for item in data
            ]
            return list(self.mapped_model.objects.filter(id__in=resolved_ids))
        else:
            obj_id = super().to_internal_value(data)
            obj = self.mapped_model.objects.get(id=obj_id)
            return obj


class IdLookupMixin:
    """
    Lookup object using default method unless int provided, then lookup by id
    """

    def to_internal_value(self, data):
        if isinstance(data, int):
            try:
                obj = self.Meta.model.objects.get(id=data)
                return obj
            except ObjectDoesNotExist as err:
                err_msg = f"Invalid id supplied for {self.Meta.model.__name__} lookup"
                raise serializers.ValidationError(err_msg) from err

        return super().to_internal_value(data)


class GetOrCreateMixin:
    """
     Class to be mixed into serializers which combines get/create functionality

    This mixin:
     1. disables any UniqueTogetherValidators
     2. overrides create to actually call get_or_create

     The end result is a serializer mixing this in can either lookup or create
     an element, so that clients can pass the same payload multiple times and get back
     consistent results (idempotency, more or less).

     To elaborate, as a use case consider a model like epi.models.Criteria;
     this contains a unique_together meta restriction on the "assessment"
     and "description" fields. Or in other words, in the database
     assessment+description are guaranteed to be unique.

     We want to build an API able to support something like a POST
     { "assessment": 1, "description": "foo" }
     to the endpoint defined for this. A normal serializer will complain
     if a criteria with that description already exists, due to the
     UniqueTogetherValidator firing. If instead we mix this class into
     the appropriate serializer, we can code things such that the first call
     will create a criteria with description "foo", and the second
     call will just fetch the existing one. This makes client construction
     just a little more straightforward -- rather than having to
     lookup/check/create-if-needed, clients can just hit one endpoint and
     get back the same object id every time.

     Basic approach taken from https://stackoverflow.com/questions/25026034/
    """

    def run_validators(self, value):
        for validator in self.validators:
            if isinstance(validator, UniqueTogetherValidator):
                self.validators.remove(validator)
        super().run_validators(value)

    def create(self, validated_data, *args, **kwargs):
        instance, _created = self.Meta.model.objects.get_or_create(**validated_data)
        return instance


class FlexibleFieldsMixin:
    """
    Allows manipulation of fields on serializer instances.
    This mixin is primarily meant for serialization and not deserialization.

    Constructor kwargs:
        fields (list[str]): allowlist of field names to include in serializer
        field_prefix (str): prefix to add to all field names
        field_renames (dict): mapping of old field names to new field names
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        field_prefix = kwargs.pop("field_prefix", "")
        field_renames = kwargs.pop("field_renames", {})

        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if not field_prefix and not field_renames:
            # If nothing else needs to be done, return
            return

        # 'fields' is a BindingDict, which has an underlying dict.
        # any changes require it to be rebuilt to maintain its order.
        for field_name in list(self.fields):
            if field_name in field_renames:
                # handle renames
                new_field_name = field_renames[field_name]
                if field_name == new_field_name:
                    # special case; assign on the underlying dict to avoid error on BindingDict __setitem__
                    self.fields.fields[field_name] = self.fields.pop(field_name)
                else:
                    self.fields[new_field_name] = self.fields.pop(field_name)
            elif field_prefix:
                # handle prefixes
                self.fields[field_prefix + field_name] = self.fields.pop(field_name)
            else:
                # handle case of no rename or prefix
                self.fields.fields[field_name] = self.fields.pop(field_name)


class BulkSerializer(serializers.ListSerializer):
    """
    Bulk create/update serializer for many = True
    "id" must be given write access on serializer for bulk update
    (eg.  id = IntegerField(required=False))
    """

    def to_internal_value(self, data):
        """
        This is the inherited method from ListSerializer, with a changes.
        `exclude_current_instance` on `UniqueValidator` examines the `instance` set on the
        serializer to exclude it from the uniqueness constraint:
        https://github.com/encode/django-rest-framework/blob/3875d3284e73ed4d8e36c07d9b70c1b22c9d5998/rest_framework/validators.py#L138
        However, `instance` in this case is the queryset passed in to the constructor, so it
        throws an error when it attempts to retrieve the `pk` attribute of the queryset.
        The fix is to set the correct `instance` before validation is run.

        Further description of issue and fix:
        https://github.com/encode/django-rest-framework/issues/6130
        https://github.com/miki725/django-rest-framework-bulk/issues/68
        """
        if html.is_html_input(data):
            data = html.parse_html_list(data, default=[])

        if not isinstance(data, list):
            message = self.error_messages["not_a_list"].format(input_type=type(data).__name__)
            raise serializers.ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: [message]}, code="not_a_list"
            )

        if not self.allow_empty and len(data) == 0:
            message = self.error_messages["empty"]
            raise serializers.ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: [message]}, code="empty"
            )

        ret = []
        errors = []

        for item in data:
            try:
                # Inserted code
                self.child.instance = self.instance.get(id=item["id"]) if self.instance else None
                self.child.initial_data = item
                # End inserted code
                validated = self.child.run_validation(item)
            except serializers.ValidationError as exc:
                errors.append(exc.detail)
            else:
                ret.append(validated)
                errors.append({})

        if any(errors):
            raise serializers.ValidationError(errors)

        return ret

    def validate_update(self, data):
        """
        Validates data for bulk update operation.
        """
        # ids must be in data
        data_ids = set([obj_data.get("id") for obj_data in data])
        if None in data_ids:
            raise serializers.ValidationError("'id' is required to map to instance.")
        # all data ids should be in instance
        instance_ids = set([obj.id for obj in self.instance])
        invalid_data_ids = data_ids - instance_ids
        if invalid_data_ids:
            raise serializers.ValidationError(
                f"Invalid 'id's: {', '.join([str(_) for _ in invalid_data_ids])}."
            )

    def validate_create(self, data):
        """
        Validates data for bulk create operation.
        """
        # ids must not be in data
        if any("id" in obj_data for obj_data in data):
            raise serializers.ValidationError("'id' is prohibited.")

    def validate(self, data):
        """
        Validates data.

        If the serializer has an `instance`, then the data is validated for bulk update on that `instance`.
        Otherwise it is validated for bulk create.
        """
        # if instance is set, its an update
        if self.instance is not None:
            self.validate_update(data)
        # otherwise its a create
        else:
            self.validate_create(data)

        return data

    def values_equal(self, instance, field, value) -> bool:
        """
        Returns whether the value of an instance field and another given value are equal.

        Args:
            instance (Model): model instance
            field (str): field name
            value (Any): value to equate

        Returns:
            bool: equality of instance field value and given value
        """
        return getattr(instance, field) == value

    def update_fields(self, instance, data) -> tuple[bool, list]:
        """
        Attempts to update an instance with given data.

        Args:
            instance (Model): model instance
            data (dict): serialized instance data

        Returns:
            tuple[bool, list]: a tuple of whether the instance has been updated, and a list of updated fields
        """
        fields = list(data.keys())
        fields.remove("id")
        updated_fields = []
        for field in fields:
            value = data[field]
            if not self.values_equal(instance, field, value):
                setattr(instance, field, value)
                updated_fields.append(field)
        requires_update = bool(updated_fields)
        if requires_update and hasattr(instance, "last_updated"):
            instance.last_updated = timezone.now()
            updated_fields.append("last_updated")
        return requires_update, updated_fields

    def update(self, instances, validated_data):
        """
        Bulk update.
        """
        updated_instances = []
        updated_fields = set()
        instance_mapping = {instance.id: instance for instance in instances}
        for data in validated_data:
            instance = instance_mapping.get(data["id"])
            updated, fields = self.update_fields(instance, data)
            if updated:
                updated_instances.append(instance)
                updated_fields.update(fields)
        Model = self.child.Meta.model
        if updated_instances:
            Model.objects.bulk_update(updated_instances, updated_fields)
        return updated_instances

    def create(self, validated_data):
        """
        Bulk create.
        """
        Model = self.child.Meta.model
        instances = [Model(**data) for data in validated_data]
        return Model.objects.bulk_create(instances)


class PydanticDrfSerializer(BaseModel):
    @classmethod
    def from_drf(cls, data: dict | QueryDict, **extras):
        """Generate an instance of a Pydantic model assuming successful validation.

        Args:
            data (Union[dict, QueryDict]): request.data (POST) or request.query_params (GET)
            **extras: extra data passed to the model constructor

        Raises:
            DrfValidationError: A Django Reset Framework Validation Error in unsuccessful.
        """
        d = data
        if isinstance(data, QueryDict):
            d = data.dict()
        if extras:
            d.update(extras)
        try:
            return cls.model_validate(d)
        except PydanticError as err:
            errors = defaultdict(list)
            for e in err.errors():
                if len(e["loc"]) > 0:
                    for key in e["loc"]:
                        error_key = (
                            key if key != "__root__" and len(key) > 0 else "non_field_errors"
                        )
                        errors[error_key].append(e["msg"])
                else:
                    errors["non_field_errors"].append(e["msg"])
            raise DrfValidationError(errors) from err


class RequiredIdSerializer(serializers.Serializer):
    id = serializers.IntegerField()


def check_ids(data: list[dict]) -> list[int]:
    """Ensure data passed via a request contains a list of integers; else raise ValidationError

    Args:
        data (list): a DRF Request data object

    Returns:
        list[int]: a list of integers from the request data
    """
    ser = RequiredIdSerializer(data=data, many=True)
    ser.is_valid(raise_exception=True)
    return [int(el["id"]) for el in ser.validated_data]
