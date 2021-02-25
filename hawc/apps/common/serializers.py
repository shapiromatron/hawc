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


class ReadableChoiceField(serializers.ChoiceField):
    """
    simple field for Choices - accepts only the underlying value during writes, but returns the "readable" display during reads.
    Seems like there is probably a Django built-in way to achieve this but I couldn't figure out how...
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
            if key == data:
                return key

        self.fail("invalid_choice", input=data)


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
            # print(f"\t[{key}] -> [{val}]")
            if val == data:
                return key

            if key == data:
                return key

            # case-insensitive string matching
            if type(val) is str and type(data) is str:
                if val is not None:
                    if val.lower() == data.lower():
                        return key

        self.fail("invalid_choice", input=data)


class FlexibleDBLinkedChoiceField(FlexibleChoiceField):
    """
    like a FlexibleChoiceField, except it derives its choices from a model/database table
    and optionally supports multiples. Used for instance when:
        * linking an epi group to one or more ethnicities.
        * linking a epi result to a single metric
        * etc.
    """

    def __init__(self, mapped_model, serializer_class, field_for_descriptor, many):
        # TODO - do we need a way to refresh this if the list changes after application startup?
        self.serializer = serializer_class()
        self.many = many
        self.mapped_model = mapped_model
        mapped_objects = mapped_model.objects.all()
        db_choices = []
        for mapped_object in mapped_objects:
            loop_id = mapped_object.id
            loop_descriptor = getattr(mapped_object, field_for_descriptor)
            db_choices.append((loop_id, loop_descriptor))

        super().__init__(choices=db_choices)

    def to_representation(self, obj):
        # print(f"to_representation for {obj} / {type(obj)}")

        if self.many:
            rv = []
            for el in obj.all():
                rv.append(self.serializer.to_representation(el))
            return rv
        else:
            return self.serializer.to_representation(obj)

    def to_internal_value(self, data):
        # print(f"to_internal_value for {data} / {type(data)}")
        if self.many:
            fixed = []
            for x in data:
                resolved = super().to_internal_value(x)
                fixed.append(resolved)
            return fixed
        else:
            obj_id = super().to_internal_value(data)
            obj = self.mapped_model.objects.get(id=obj_id)
            return obj
