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
