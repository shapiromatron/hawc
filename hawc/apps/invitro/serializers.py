import json

from rest_framework import serializers

from ..assessment.api.serializers import AssessmentRootedSerializer
from ..assessment.serializers import DSSToxSerializer, EffectTagsSerializer
from ..common.api import DynamicFieldsMixin
from ..common.helper import SerializerHelper
from ..study.serializers import StudySerializer
from . import models


class IVCellTypeSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="__str__", read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    url_update = serializers.CharField(source="get_update_url", read_only=True)
    url_delete = serializers.CharField(source="get_delete_url", read_only=True)
    sex_symbol = serializers.CharField(source="get_sex_symbol", read_only=True)
    culture_type = serializers.CharField(source="get_culture_type_display", read_only=True)
    sex = serializers.CharField(source="get_sex_display", read_only=True)

    class Meta:
        model = models.IVCellType
        fields = "__all__"


class IVExperimentSerializer(serializers.ModelSerializer):
    study = StudySerializer()
    cell_type = IVCellTypeSerializer()
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    metabolic_activation = serializers.CharField(
        source="get_metabolic_activation_display", read_only=True
    )

    class Meta:
        model = models.IVExperiment
        fields = "__all__"
        depth = 1


class _IVChemicalSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    url_update = serializers.CharField(source="get_update_url", read_only=True)
    url_delete = serializers.CharField(source="get_delete_url", read_only=True)
    dtxsid = DSSToxSerializer()

    class Meta:
        model = models.IVChemical
        fields = "__all__"


class IVChemicalSerializer(_IVChemicalSerializer):
    study = StudySerializer()


class IVEndpointGroupSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["difference_control"] = instance.get_difference_control_display()
        ret["difference_control_symbol"] = instance.difference_control_symbol
        ret["significant_control"] = instance.get_significant_control_display()
        ret["cytotoxicity_observed"] = instance.get_cytotoxicity_observed_display()
        ret["precipitation_observed"] = instance.get_precipitation_observed_display()
        return ret

    class Meta:
        model = models.IVEndpointGroup
        fields = "__all__"


class IVBenchmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IVBenchmark
        fields = "__all__"


class IVEndpointCategorySerializer(AssessmentRootedSerializer):
    parent = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = models.IVEndpointCategory
        fields = ("id", "name", "parent")


class IVEndpointCategory(serializers.ModelSerializer):
    def to_representation(self, instance):
        return dict(names=instance.get_list_representation())

    class Meta:
        model = models.IVEndpointCategory
        fields = "__all__"


class IVEndpointSerializer(serializers.ModelSerializer):
    assessment = serializers.PrimaryKeyRelatedField(read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    url_update = serializers.CharField(source="get_update_url", read_only=True)
    url_delete = serializers.CharField(source="get_delete_url", read_only=True)
    chemical = _IVChemicalSerializer()
    experiment = IVExperimentSerializer()
    groups = IVEndpointGroupSerializer(many=True)
    benchmarks = IVBenchmarkSerializer(many=True)
    category = IVEndpointCategory()
    effects = EffectTagsSerializer(many=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["data_type"] = instance.get_data_type_display()
        ret["variance_type"] = instance.get_variance_type_display()
        ret["observation_time_units"] = instance.get_observation_time_units_display()
        ret["monotonicity"] = instance.get_monotonicity_display()
        ret["overall_pattern"] = instance.get_overall_pattern_display()
        ret["trend_test"] = instance.get_trend_test_display()
        ret["additional_fields"] = json.loads(instance.additional_fields)
        models.IVEndpointGroup.getStdevs(instance.variance_type, ret["groups"])
        models.IVEndpointGroup.percentControl(instance.data_type, ret["groups"])
        return ret

    class Meta:
        model = models.IVEndpoint
        fields = "__all__"


class MiniIVEndpointSerializer(serializers.ModelSerializer):
    experiment = serializers.PrimaryKeyRelatedField(read_only=True)
    chemical = _IVChemicalSerializer()
    groups = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    benchmarks = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    category = serializers.PrimaryKeyRelatedField(read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["url"] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.IVEndpoint
        fields = "__all__"


class IVExperimentSerializerFull(IVExperimentSerializer):
    url_update = serializers.CharField(source="get_update_url", read_only=True)
    url_delete = serializers.CharField(source="get_delete_url", read_only=True)
    url_create_endpoint = serializers.CharField(source="get_endpoint_create_url", read_only=True)
    endpoints = MiniIVEndpointSerializer(many=True)


class IVEndpointCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.IVEndpoint
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = (*cleanup_fields, "id")

    def get_study_short_citation(self, obj):
        return obj.experiment.study.short_citation


class IVChemicalCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.IVChemical
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = (*cleanup_fields, "id")

    def get_study_short_citation(self, obj):
        return obj.study.short_citation


SerializerHelper.add_serializer(models.IVEndpoint, IVEndpointSerializer)
