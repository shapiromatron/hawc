from typing import Dict, List

from django.db import models
from rest_framework import serializers


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
    display value when supplying data. Makes life easier on clients.
    """

    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data:
                return key

            if key == data:
                return key

            # case-insensitive string matching
            if type(val) is str and type(data) is str:
                if val is not None:
                    if val.lower() == data.lower():
                        return key

        self.fail('invalid_choice', input=data)

class FlexibleDBLinkedChoiceManyField(FlexibleChoiceField):
    """
    like a FlexibleChoiceField, except it derives its choices from a database table
    and supports multiples. Used for instance when linking an epi group to one or more ethnicities.
    """

    def __init__(self, mapped_db_table, serializer_class, field_for_descriptor):
        self.serializer = serializer_class()
        mapped_objects = mapped_db_table.objects.all()
        db_choices = []
        for mapped_object in mapped_objects:
            loop_id = mapped_object.id
            loop_descriptor = getattr(mapped_object, field_for_descriptor)
            db_choices.append((loop_id, loop_descriptor))

        super().__init__(choices=db_choices)

    def to_representation(self, obj):
        rv = []
        for el in obj.all():
            rv.append(self.serializer.to_representation(el))

        return rv

    def to_internal_value(self, data):
        fixed = []
        for x in data:
            resolved = super().to_internal_value(x)
            fixed.append(resolved)

        return fixed
