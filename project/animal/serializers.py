import json

from rest_framework import serializers

from assessment.serializers import EffectTagsSerializer

from bmd.serializers import BMDModelRunSerializer
from riskofbias.serializers import RiskOfBiasSerializer
from study.serializers import StudySerializer
from utils.api import DynamicFieldsMixin
from utils.helper import SerializerHelper

from . import models


class ExperimentSerializer(serializers.ModelSerializer):
    study = StudySerializer()

    def to_representation(self, instance):
        ret = super(ExperimentSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        ret['type'] = instance.get_type_display()
        ret['litter_effects'] = instance.get_litter_effects_display()
        ret['is_generational'] = instance.is_generational()
        ret['cas_url'] = instance.cas_url
        return ret

    class Meta:
        model = models.Experiment


class DosesSerializer(serializers.ModelSerializer):
    dose_regime = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.DoseGroup
        depth = 1


class AnimalGroupRelationSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super(AnimalGroupRelationSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.AnimalGroup
        fields = ('id', 'name', )


class DosingRegimeSerializer(serializers.ModelSerializer):
    doses = DosesSerializer(many=True)
    dosed_animals = AnimalGroupRelationSerializer()

    def to_representation(self, instance):
        ret = super(DosingRegimeSerializer, self).to_representation(instance)
        ret['route_of_exposure'] = instance.get_route_of_exposure_display()
        ret['positive_control'] = instance.get_positive_control_display()
        ret['negative_control'] = instance.get_negative_control_display()
        return ret

    class Meta:
        model = models.DosingRegime


class AnimalGroupSerializer(serializers.ModelSerializer):
    experiment = ExperimentSerializer()
    dosing_regime = DosingRegimeSerializer(allow_null=True)
    species = serializers.StringRelatedField()
    strain = serializers.StringRelatedField()
    parents = AnimalGroupRelationSerializer(many=True)
    siblings = AnimalGroupRelationSerializer()
    children = AnimalGroupRelationSerializer(many=True)

    def to_representation(self, instance):
        ret = super(AnimalGroupSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        ret['sex'] = instance.get_sex_display()
        ret['generation'] = instance.generation_short
        ret['sex_symbol'] = instance.sex_symbol
        return ret

    class Meta:
        model = models.AnimalGroup


class EndpointGroupSerializer(serializers.ModelSerializer):
    endpoint = serializers.PrimaryKeyRelatedField(read_only=True)

    def to_representation(self, instance):
        ret = super(EndpointGroupSerializer, self).to_representation(instance)
        ret['hasVariance'] = instance.hasVariance
        ret['isReported'] = instance.isReported
        return ret

    class Meta:
        model = models.EndpointGroup


class EndpointSerializer(serializers.ModelSerializer):
    assessment = serializers.PrimaryKeyRelatedField(read_only=True)
    effects = EffectTagsSerializer()
    animal_group = AnimalGroupSerializer()
    groups = EndpointGroupSerializer(many=True)
    qualities = RiskOfBiasSerializer(many=True, read_only=True)

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
        models.EndpointGroup.getStdevs(ret['variance_type'], ret['groups'])
        models.EndpointGroup.percentControl(ret['data_type'], ret['groups'])

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


class CleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = models.Endpoint
        cleanup_fields = model.text_cleanup_fields()
        fields = cleanup_fields + ('id', 'name')

SerializerHelper.add_serializer(models.Endpoint, EndpointSerializer)
