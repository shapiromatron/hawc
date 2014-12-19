import json

from rest_framework import serializers

from assessment.serializers import EffectTagsSerializer

from utils.helper import SerializerHelper
from study.serializers import StudySerializer
from bmd.serializers import BMDModelRunSerializer

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
    parents = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

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


class UncertaintyFactorEndpointSerializer(serializers.ModelSerializer):
    endpoint = serializers.PrimaryKeyRelatedField(read_only=True)

    def to_representation(self, instance):
        ret = super(UncertaintyFactorEndpointSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        ret['uf_type_verbose'] = instance.get_uf_type_display()
        return ret

    class Meta:
        model = models.UncertaintyFactorEndpoint


class EndpointSerializer(serializers.ModelSerializer):
    assessment = serializers.PrimaryKeyRelatedField(read_only=True)
    effects = EffectTagsSerializer()
    animal_group = AnimalGroupSerializer()
    endpoint_group = EndpointGroupSerializer(many=True)
    ufs = UncertaintyFactorEndpointSerializer(many=True)

    def to_representation(self, instance):
        ret = super(EndpointSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        ret['dataset_increasing'] = instance.dataset_increasing
        ret['variance_name'] = instance.variance_name
        ret['data_type_label'] = instance.get_data_type_display()
        ret['observation_time_units'] = instance.get_observation_time_units_display()
        ret['monotonicity'] = instance.get_monotonicity_display()
        ret['trend_result'] = instance.get_trend_result_display()
        ret['additional_fields'] = json.loads(instance.additional_fields)
        models.EndpointGroup.getStdevs(ret['variance_type'], ret['endpoint_group'])
        models.EndpointGroup.percentControl(ret['data_type'], ret['endpoint_group'])

        # get individual animal data
        if instance.individual_animal_data:
            models.EndpointGroup.getIndividuals(instance, ret['endpoint_group'])

        # get BMD
        ret['BMD'] = None
        try:
            model = instance.BMD_session.latest().selected_model
            if model is not None:
                ret['BMD'] = BMDModelRunSerializer().to_representation(model)
        except instance.BMD_session.model.DoesNotExist:
            pass

        return ret

    class Meta:
        model = models.Endpoint


SerializerHelper.add_serializer(models.Endpoint, EndpointSerializer)
