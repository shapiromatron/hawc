import json

from rest_framework import serializers

from assessment.serializers import EffectTagsSerializer

from utils.helper import SerializerHelper
from study.serializers import StudySerializer

from . import models


class ExperimentSerializer(serializers.ModelSerializer):
    study = StudySerializer()

    def to_representation(self, instance):
        ret = super(ExperimentSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        ret['type'] = instance.get_type_display()
        return ret

    class Meta:
        model = models.Experiment


class DosesSerializer(serializers.ModelSerializer):
    dose_regime = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.DoseGroup
        depth = 1


class DosingRegimeSerializer(serializers.ModelSerializer):
    doses = DosesSerializer(many=True)

    def to_representation(self, instance):
        ret = super(DosingRegimeSerializer, self).to_representation(instance)
        ret['route_of_exposure'] = instance.get_route_of_exposure_display()
        return ret

    class Meta:
        model = models.DosingRegime


class AnimalGroupSerializer(serializers.ModelSerializer):
    experiment = ExperimentSerializer()
    dosing_regime = DosingRegimeSerializer(allow_null=True)
    species = serializers.StringRelatedField()
    strain = serializers.StringRelatedField()

    def to_representation(self, instance):
        ret = super(AnimalGroupSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        ret['sex'] = instance.get_sex_display()
        return ret

    class Meta:
        model = models.AnimalGroup


class EndpointGroupSerializer(serializers.ModelSerializer):
    endpoint = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.EndpointGroup


class EndpointSerializer(serializers.ModelSerializer):
    assessment = serializers.PrimaryKeyRelatedField(read_only=True)
    effects = EffectTagsSerializer()
    animal_group = AnimalGroupSerializer()
    endpoint_group = EndpointGroupSerializer(many=True)

    def to_representation(self, instance):
        ret = super(EndpointSerializer, self).to_representation(instance)
        ret['dataset_increasing'] = instance.dataset_increasing
        ret['variance_name'] = instance.variance_name
        ret['observation_time_units'] = instance.get_observation_time_units_display()
        ret['monotonicity'] = instance.get_monotonicity_display()
        ret['additional_fields'] = json.loads(instance.additional_fields)
        models.EndpointGroup.getStdevs(ret['variance_type'], ret['endpoint_group'])
        models.EndpointGroup.percentControl(ret['data_type'], ret['endpoint_group'])

        if instance.individual_animal_data:
            models.EndpointGroup.getIndividuals(instance, ret['endpoint_group'])

        return ret

    class Meta:
        model = models.Endpoint



SerializerHelper.add_serializer(models.Endpoint, EndpointSerializer)
