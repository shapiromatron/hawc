import json

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions, serializers

from ..assessment.serializers import EffectTagsSerializer
from ..bmd.serializers import ModelSerializer
from ..common.api import DynamicFieldsMixin
from ..common.helper import SerializerHelper
from ..study.models import Study
from ..study.serializers import StudySerializer
from . import models


class ExperimentSerializer(serializers.ModelSerializer):
    study = StudySerializer(required=False, read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["url"] = instance.get_absolute_url()
        ret["type"] = instance.get_type_display()
        ret["is_generational"] = instance.is_generational()
        ret["cas_url"] = instance.get_casrn_url()
        return ret

    def validate(self, data):
        if "study_id" in self.initial_data:
            # Get study instance
            study_id = self.initial_data.get("study_id")
            try:
                study = Study.objects.get(id=study_id)
                data["study"] = StudySerializer(study).data
            except ValueError:
                raise serializers.ValidationError("Study ID must be a number.")
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Study ID does not exist.")
        elif "study" in self.initial_data:
            study_serializer = StudySerializer(data=self.initial_data.get("study"))
            study_serializer.is_valid(raise_exception=True)
            data["study"] = study_serializer.validated_data
        else:
            # Serializer needs one form of study identifier
            raise serializers.ValidationError("Expected 'study' or 'study_id'.")
        return super().validate(data)

    def create(self, validated_data):
        study_id = self.initial_data.get("study_id")
        study = Study.objects.get(id=study_id)
        if not study.assessment.user_can_edit_object(self.context["request"].user):
            raise exceptions.PermissionDenied("Invalid permission to edit assessment.")
        validated_data["study"] = study
        return models.Experiment.objects.create(**validated_data)

    class Meta:
        model = models.Experiment
        fields = "__all__"


class DosesSerializer(serializers.ModelSerializer):
    dose_regime = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.DoseGroup
        fields = "__all__"
        depth = 1


class AnimalGroupRelationSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["url"] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.AnimalGroup
        fields = (
            "id",
            "name",
        )


class DosingRegimeSerializer(serializers.ModelSerializer):
    doses = DosesSerializer(many=True)
    dosed_animals = AnimalGroupRelationSerializer()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["route_of_exposure"] = instance.get_route_of_exposure_display()
        ret["positive_control"] = instance.get_positive_control_display()
        ret["negative_control"] = instance.get_negative_control_display()
        return ret

    class Meta:
        model = models.DosingRegime
        fields = "__all__"


class AnimalGroupSerializer(serializers.ModelSerializer):
    experiment = ExperimentSerializer()
    dosing_regime = DosingRegimeSerializer(allow_null=True)
    species = serializers.StringRelatedField()
    strain = serializers.StringRelatedField()
    parents = AnimalGroupRelationSerializer(many=True)
    siblings = AnimalGroupRelationSerializer()
    children = AnimalGroupRelationSerializer(many=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["url"] = instance.get_absolute_url()
        ret["sex"] = instance.get_sex_display()
        ret["generation"] = instance.generation_short
        ret["sex_symbol"] = instance.sex_symbol
        return ret

    class Meta:
        model = models.AnimalGroup
        fields = "__all__"


class EndpointGroupSerializer(serializers.ModelSerializer):
    endpoint = serializers.PrimaryKeyRelatedField(read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["hasVariance"] = instance.hasVariance
        ret["isReported"] = instance.isReported
        return ret

    class Meta:
        model = models.EndpointGroup
        fields = "__all__"


class EndpointSerializer(serializers.ModelSerializer):
    assessment = serializers.PrimaryKeyRelatedField(read_only=True)
    effects = EffectTagsSerializer()
    animal_group = AnimalGroupSerializer()
    groups = EndpointGroupSerializer(many=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret["url"] = instance.get_absolute_url()
        ret["dataset_increasing"] = instance.dataset_increasing
        ret["variance_name"] = instance.variance_name
        ret["data_type_label"] = instance.get_data_type_display()
        ret["observation_time_units"] = instance.get_observation_time_units_display()
        ret[
            "expected_adversity_direction_text"
        ] = instance.get_expected_adversity_direction_display()
        ret["monotonicity"] = instance.get_monotonicity_display()
        ret["trend_result"] = instance.get_trend_result_display()
        ret["additional_fields"] = json.loads(instance.additional_fields)
        ret["litter_effects_display"] = instance.get_litter_effects_display()
        ret["experiment_type"] = instance.animal_group.experiment.type
        ret["noel_names"] = instance.get_noel_names()._asdict()
        models.EndpointGroup.getStdevs(ret["variance_type"], ret["groups"])
        models.EndpointGroup.percentControl(ret["data_type"], ret["groups"])
        models.EndpointGroup.getConfidenceIntervals(ret["data_type"], ret["groups"])
        models.EndpointGroup.get_incidence_summary(ret["data_type"], ret["groups"])
        models.Endpoint.setMaximumPercentControlChange(ret)

        ret["bmd"] = None
        ret["bmd_notes"] = ""
        ret["bmd_url"] = ""
        selected_model = instance.get_selected_bmd_model()
        if selected_model:
            ret["bmd_notes"] = selected_model.notes
            if selected_model.model_id is not None:
                ret["bmd"] = ModelSerializer().to_representation(selected_model.model)
            else:
                ret["bmd_url"] = instance.bmd_sessions.latest().get_absolute_url()

        return ret

    class Meta:
        model = models.Endpoint
        fields = "__all__"


class ExperimentCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Experiment
        cleanup_fields = ("study_short_citation",) + model.TEXT_CLEANUP_FIELDS
        fields = cleanup_fields + ("id",)

    def get_study_short_citation(self, obj):
        return obj.study.short_citation


class AnimalGroupCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.AnimalGroup
        cleanup_fields = ("study_short_citation",) + model.TEXT_CLEANUP_FIELDS
        fields = cleanup_fields + ("id",)

    def get_study_short_citation(self, obj):
        return obj.experiment.study.short_citation


class EndpointCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Endpoint
        cleanup_fields = ("study_short_citation",) + model.TEXT_CLEANUP_FIELDS
        fields = cleanup_fields + ("id",)

    def get_study_short_citation(self, obj):
        return obj.animal_group.experiment.study.short_citation


class DosingRegimeCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.DosingRegime
        cleanup_fields = ("study_short_citation",) + model.TEXT_CLEANUP_FIELDS
        fields = cleanup_fields + ("id",)

    def get_study_short_citation(self, obj):
        return obj.dosed_animals.experiment.study.short_citation


SerializerHelper.add_serializer(models.Endpoint, EndpointSerializer)
