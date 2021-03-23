from typing import Any, Dict, List, Type

import pydantic
from django.core.exceptions import ValidationError
from django.db import models
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer


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
    like a ChoiceField, except it will let you specify either the raw choice value OR a case-insensitive
    display value when supplying data. Makes client code simpler/more readable.
    """

    def to_representation(self, obj):
        if obj == "" and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == "" and self.allow_blank:
            return ""

        for key, val in self._choices.items():
            if key == data or val == data:
                return key

        # no exact match; if a string was passed in let's try case-insensitive value match
        if type(data) is str:
            lowered_data = data.lower()
            for key, val in self._choices.items():
                if val is not None and str(val).lower() == lowered_data:
                    return key

        self.fail("invalid_choice", input=data)


# reworked this; neest to test AWS
class FlexibleDBLinkedChoiceField(FlexibleChoiceField):
    """
    like a FlexibleChoiceField, except it derives its choices from a model/database table
    and optionally supports multiples. Used for instance when:
        * linking an epi group to one or more ethnicities.
        * linking a epi result to a single metric
        * etc.
    """

    def __init__(self, mapped_model, serializer_class, field_for_descriptor, many):
        super().__init__(choices=[])
        self.serializer = serializer_class()
        self.mapped_model = mapped_model
        self.field_for_descriptor = field_for_descriptor
        self.many = many
        self.related_objects_loaded = False

    def load_related_objects_if_needed(self, force_reload=False):
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
            rv = []
            for el in obj.all():
                rv.append(self.serializer.to_representation(el))
            return rv
        else:
            return self.serializer.to_representation(obj)

    def to_internal_value(self, data):
        self.load_related_objects_if_needed()

        if self.many:
            # super() doesn't work inside list comprehensions; could this leverage __class__ somehow?
            # resolved_ids = [super().to_internal_value(x) for x in data]
            # for now we'll just write the loop by hand.

            resolved_ids = []
            for raw_input_el in data:
                # each element could be an id or a readable value, so first we convert to id
                resolved_ids.append(super().to_internal_value(raw_input_el))

            # and now we return the actual objects in a list
            return list(self.mapped_model.objects.filter(id__in=resolved_ids))
        else:
            obj_id = super().to_internal_value(data)
            obj = self.mapped_model.objects.get(id=obj_id)
            return obj
