import json

from rest_framework import serializers
from rest_framework.exceptions import ParseError

from utils.helper import SerializerHelper
from study.serializers import StudySerializer

from . import models


class ExperimentSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    study = StudySerializer()

    def transform_type(self, obj, value):
        return obj.get_type_display()

    class Meta:
        model = models.Experiment


class DosesSerializer(serializers.ModelSerializer):
    dose_regime = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = models.DoseGroup
        depth = 1


class DosingRegimeSerializer(serializers.ModelSerializer):
    doses = DosesSerializer()

    def transform_route_of_exposure(self, obj, value):
        return obj.get_route_of_exposure_display()

    class Meta:
        model = models.DosingRegime


class AnimalGroupSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    experiment = ExperimentSerializer()
    dosing_regime = DosingRegimeSerializer()

    def transform_sex(self, obj, value):
        return obj.get_sex_display()

    class Meta:
        model = models.AnimalGroup
        depth = 1


class EffectTagsSerializer(serializers.WritableField):
    # http://blog.pedesen.de/2013/07/06/Using-django-rest-framework-with-tagged-items-django-taggit/

    def from_native(self, data):
        raise ParseError("Write-not implemented")

    def to_native(self, obj):
        if type(obj) is not list:
            return [{"slug": tag.slug, "name": tag.name} for tag in obj.all()]
        return obj


class EndpointGroupSerializer(serializers.ModelSerializer):
    endpoint = serializers.PrimaryKeyRelatedField()
    stdev = serializers.FloatField(source='getStdev', read_only=True)

    class Meta:
        model = models.EndpointGroup


class EndpointSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    assessment = serializers.PrimaryKeyRelatedField()
    effects = EffectTagsSerializer()
    animal_group = AnimalGroupSerializer()
    endpoint_group = EndpointGroupSerializer()

    def transform_observation_time_units(self, obj, value):
        return obj.get_observation_time_units_display()

    def transform_monotonicity(self, obj, value):
        return obj.get_monotonicity_display()

    def transform_additional_fields(self, obj, value):
        return json.loads(obj.additional_fields)

    class Meta:
        model = models.Endpoint


SerializerHelper.add_serializer(models.Endpoint, EndpointSerializer)
