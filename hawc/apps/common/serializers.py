from datetime import datetime
from typing import Any, Dict, List, Tuple, Type

import jsonschema
import pydantic
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.settings import api_settings
from rest_framework.utils import html
from rest_framework.validators import UniqueTogetherValidator

from .helper import get_id_from_choices


def to_json(Serializer: serializers.ModelSerializer, instance: models.Model) -> str:
    """Return a JSON string from an instance just like a serializer would, outside of the drf view logic.

    Args:
        Serializer (serializers.ModelSerializer): a django model serializer class
        instance (models.Model): a django model instance

    Returns:
        str: a JSON string representation
    """
    serializer = Serializer(instance=instance)
    return JSONRenderer().render(serializer.data).decode("utf8")


def validate_pydantic(
    pydantic_class: Type[pydantic.BaseModel], field: str, data: Any
) -> pydantic.BaseModel:
    """Validation helper to validate a field to a pydnatic model.

    Args:
        pydantic_class (pydantic.BaseModel): A Pydantic base class
        field (str): the field to raise the error on
        data (Any): the data to be validated

    Raises:
        ValidationError: a Django Validation error

    Returns:
        pydantic.BaseModel: The pydantic BaseModel
    """
    try:
        return pydantic_class.parse_obj(data)
    except pydantic.ValidationError as err:
        raise ValidationError({field: err.json()})


class UnusedSerializer(serializers.Serializer):
    """
    Nondescript serializer. Used in instances where a view does not use a serializer
    but one needs to be set, such as for OpenAPI generation.
    """

    pass


class HeatmapQuerySerializer(serializers.Serializer):
    unpublished = serializers.BooleanField(default=False)


def get_matching_instance(Model: models.Model, data: Dict, field_name: str) -> models.Model:
    """
    Return a matching django model object or throw ValidationError if not found.

    Args:
        model: (models.Model): The model to fetch an instance of
        data (Dict): the data dictionary
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
    except ValueError:
        err[field_name] = f"`{field_name} must be a number; got {id_}."
        raise serializers.ValidationError(err)
    except models.ObjectDoesNotExist:
        err[field_name] = f"{Model.__name__} {id_} does not exist."
        raise serializers.ValidationError(err)


def get_matching_instances(Model: models.Model, data: Dict, field_name: str) -> List[models.Model]:
    """
    Return a matching django models list or throw ValidationError if not found.

    Args:
        model: (models.Model): The model to fetch an instance of
        data (Dict): the data dictionary
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
        except ValueError:
            err[field_name] = f"`{field_name} must be a number; got {id_}."
            raise serializers.ValidationError(err)
        except models.ObjectDoesNotExist:
            err[field_name] = f"{Model.__name__} {id_} does not exist."
            raise serializers.ValidationError(err)

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
        if type(data) is str:
            key = get_id_from_choices(self._choices.items(), data)
            if key is not None:
                return key

        self.fail("invalid_choice", input=data)


class FlexibleDBLinkedChoiceField(FlexibleChoiceField):
    """
    FlexibleChoiceField subclass which derives its choices from a model/database table and optionally supports multiples.

    Used for instance when:
        * linking an epi group to one or more ethnicities.
        * linking a epi result to a single metric
        * etc.
    """

    def __init__(
        self,
        mapped_model: models.Model,
        serializer_class: serializers.ModelSerializer,
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
            # super() doesn't work inside list comprehensions; could this leverage __class__ somehow?
            # resolved_ids = [super().to_internal_value(x) for x in data]
            # for now just write the loop by hand.

            resolved_ids = []
            for raw_input_el in data:
                # Each element could be an id or a readable value, so first we convert to id
                resolved_ids.append(super().to_internal_value(raw_input_el))

            # And now we return the actual objects in a list
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
        if type(data) is int:
            try:
                obj = self.Meta.model.objects.get(id=data)
                return obj
            except ObjectDoesNotExist:
                err_msg = f"Invalid id supplied for {self.Meta.model.__name__} lookup"
                raise serializers.ValidationError(err_msg)

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
        instance, created = self.Meta.model.objects.get_or_create(**validated_data)
        return instance


class BulkSerializer(serializers.ListSerializer):
    """
    Bulk create/update serializer for many = True
    "id" must be given write access on serializer for bulk update
    (eg.  id = IntegerField(required=False))
    """

    schema = {
        "type": "array",
        "items": {"type": "object"},
    }

    def to_internal_value(self, data):
        """
        List of dicts of native values <- List of dicts of primitive datatypes.
        """
        if html.is_html_input(data):
            data = html.parse_html_list(data, default=[])

        if not isinstance(data, list):
            message = self.error_messages["not_a_list"].format(input_type=type(data).__name__)
            raise ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [message]}, code="not_a_list")

        if not self.allow_empty and len(data) == 0:
            message = self.error_messages["empty"]
            raise ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [message]}, code="empty")

        ret = []
        errors = []

        for item in data:
            try:
                # https://github.com/miki725/django-rest-framework-bulk/issues/68#issuecomment-361895823
                self.child.instance = (
                    next((_ for _ in self.instance if _.id == item.get("id")), None)
                    if self.instance
                    else None
                )
                validated = self.child.run_validation(item)
            except ValidationError as exc:
                errors.append(exc.detail)
            else:
                ret.append(validated)
                errors.append({})

        if any(errors):
            raise ValidationError(errors)

        return ret

    def validate_update(self, data):
        # ids must be in data
        data_ids = [obj_data.get("id") for obj_data in data if obj_data.get("id") is not None]
        if len(data_ids) != len(data):
            raise serializers.ValidationError("'id' is required to map to instance.")
        # all data ids should be in instance
        instance_ids = [obj.id for obj in self.instance]
        invalid_data_ids = set(data_ids) - set(instance_ids)
        if invalid_data_ids:
            raise serializers.ValidationError(
                f"Invalid 'id's: {', '.join([str(_) for _ in invalid_data_ids])}."
            )

    def validate_create(self, data):
        data_ids = [obj_data.get("id") for obj_data in data if obj_data.get("id") is not None]
        if data_ids:
            raise serializers.ValidationError("'id' is prohibited.")

    def validate(self, data):
        # enforce schema for bulk operations
        try:
            jsonschema.validate(self.initial_data, self.schema)
        except jsonschema.ValidationError as err:
            raise serializers.ValidationError(err.message)
        # ids needed for update operation
        if self.instance is not None:
            self.validate_update(data)
        # ids forbidden for create operation
        else:
            self.validate_create(data)

        return data

    def values_equal(self, instance, field, value) -> bool:
        return getattr(instance, field) == value

    def update_field(self, instance, field, value) -> str:
        setattr(instance, field, value)
        return field

    def update_fields(self, instance, data) -> Tuple[bool, List]:
        fields = list(data.keys())
        fields.remove("id")
        updated_fields = []
        for field in fields:
            value = data[field]
            if not self.values_equal(instance, field, value):
                set_field = self.update_field(instance, field, value)
                updated_fields.append(set_field)
        updated = bool(updated_fields)
        if updated and hasattr(instance, "last_updated"):
            instance.last_updated = datetime.now()
            updated_fields.append("last_updated")
        return updated, updated_fields

    def update(self, instances, validated_data):
        updated_instances = []
        updated_fields = set()
        for data in validated_data:
            instance = next(instance for instance in instances if instance.id == data["id"])
            updated, fields = self.update_fields(instance, data)
            if updated:
                updated_instances.append(instance)
                updated_fields.update(fields)
        Model = self.child.Meta.model
        if updated_instances:
            Model.objects.bulk_update(updated_instances, updated_fields)
        return updated_instances

    def create(self, validated_data):
        Model = self.child.Meta.model
        instances = [Model(**data) for data in validated_data]
        return Model.objects.bulk_create(instances)
