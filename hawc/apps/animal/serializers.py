import json

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions, serializers

from ..assessment.models import DoseUnits
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

    def validate(self, data):
        if hasattr(self, "initial_data"):
            try:
                dose_regime_id = self.initial_data.get("dose_regime_id", -1)
                models.DosingRegime.objects.get(id=dose_regime_id)
                data["dose_regime_id"] = dose_regime_id
            except ValueError:
                raise serializers.ValidationError("Dosing regime ID must be a number.")
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Dosing regime ID does not exist.")

            try:
                dose_units_id = self.initial_data.get("dose_units_id", -1)
                DoseUnits.objects.get(id=dose_units_id)
                data["dose_units_id"] = dose_units_id
            except ValueError:
                raise serializers.ValidationError("Dose units ID must be a number.")
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Dose units ID does not exist.")

        return super().validate(data)


class AnimalGroupRelationSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["url"] = instance.get_absolute_url()
        return ret

    def validate(self, data):
        if hasattr(self, "initial_data"):
            if "id" not in self.initial_data:
                raise serializers.ValidationError("ID required.")
        return super().validate(data)

    class Meta:
        model = models.AnimalGroup
        fields = (
            "id",
            "name",
        )
        extra_kwargs = {"id": {"required": True}}


class DosingRegimeSerializer(serializers.ModelSerializer):
    doses = DosesSerializer(many=True)
    dosed_animals = AnimalGroupRelationSerializer(required=False)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["route_of_exposure"] = instance.get_route_of_exposure_display()
        ret["positive_control"] = instance.get_positive_control_display()
        ret["negative_control"] = instance.get_negative_control_display()
        return ret

    def create(self, validated_data):

        doses = list()
        validated_data.pop("doses")
        dosing_regime = models.DosingRegime.objects.create(**validated_data)
        doses_data = self.initial_data.get("doses")
        for dose in doses_data:
            dose["dose_regime_id"] = dosing_regime.id
            dose_serializer = DosesSerializer(data=dose)
            dose_serializer.is_valid(raise_exception=True)
            doses.append(dose_serializer)
        # All doses are valid
        for dose in doses:
            dose.save()
        return dosing_regime

    class Meta:
        model = models.DosingRegime
        fields = "__all__"


class AnimalGroupSerializer(serializers.ModelSerializer):
    experiment = ExperimentSerializer(required=False)
    dosing_regime = DosingRegimeSerializer(allow_null=True, default=None)
    parents = AnimalGroupRelationSerializer(many=True, required=False)
    siblings = AnimalGroupRelationSerializer(required=False)
    children = AnimalGroupRelationSerializer(many=True, required=False)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["species"] = instance.species.name
        ret["strain"] = instance.strain.name
        ret["url"] = instance.get_absolute_url()
        ret["sex"] = instance.get_sex_display()
        ret["generation"] = instance.generation_short
        ret["sex_symbol"] = instance.sex_symbol
        return ret

    def validate(self, data):
        # Validate experiment
        if "experiment_id" in self.initial_data:
            # Get experiment instance
            experiment_id = self.initial_data.get("experiment_id")
            try:
                experiment = models.Experiment.objects.get(id=experiment_id)
                data["experiment"] = ExperimentSerializer(experiment).data
            except ValueError:
                raise serializers.ValidationError("Experiment ID must be a number.")
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Experiment ID does not exist.")
        elif "experiment" in self.initial_data:
            experiment_serializer = ExperimentSerializer(data=self.initial_data.get("experiment"))
            experiment_serializer.is_valid(raise_exception=True)
            data["experiment"] = experiment_serializer.validated_data
        else:
            # Serializer needs one form of experiment identifier
            raise serializers.ValidationError("Expected 'experiment' or 'experiment_id'.")

        if "dosing_regime_id" in self.initial_data:
            # Get dosing regime instance
            dosing_regime_id = self.initial_data.get("dosing_regime_id")
            try:
                dosing_regime = models.DosingRegime.objects.get(id=dosing_regime_id)
                data["dosing_regime"] = DosingRegimeSerializer(dosing_regime).data
            except ValueError:
                raise serializers.ValidationError("Dosing regime ID must be a number.")
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Dosing regime ID does not exist.")

        if "sibling_id" in self.initial_data:
            # Get animal group instance
            sibling_id = self.initial_data.get("sibling_id")
            try:
                sibling = models.AnimalGroup.objects.get(id=sibling_id)
                data["siblings"] = AnimalGroupRelationSerializer(sibling).data
            except ValueError:
                raise serializers.ValidationError("Sibling ID must be a number.")
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Sibling ID does not exist.")
        elif "siblings" in self.initial_data:
            sibling_serializer = AnimalGroupRelationSerializer(
                data=self.initial_data.get("siblings")
            )
            sibling_serializer.is_valid(raise_exception=True)
            data["siblings"] = sibling_serializer.validated_data

        return super().validate(data)

    def create(self, validated_data):
        experiment_id = self.initial_data.get("experiment_id")
        experiment = models.Experiment.objects.get(id=experiment_id)
        if not experiment.study.assessment.user_can_edit_object(self.context["request"].user):
            raise exceptions.PermissionDenied("Invalid permission to edit assessment.")
        validated_data["experiment"] = experiment
        validated_data["siblings"] = (
            models.AnimalGroup.objects.get(id=validated_data["siblings"]["id"])
            if "siblings" in validated_data
            else None
        )
        if "dosing_regime_id" in self.initial_data:
            dosing_regime_id = self.initial_data.get("dosing_regime_id")
            validated_data["dosing_regime"] = models.DosingRegime.objects.get(id=dosing_regime_id)
        elif validated_data["dosing_regime"] is not None:
            dosing_regime_serializer = DosingRegimeSerializer(
                data=self.initial_data.get("dosing_regime")
            )
            dosing_regime_serializer.is_valid(raise_exception=True)
            validated_data["dosing_regime"] = dosing_regime_serializer.save()
        return models.AnimalGroup.objects.create(**validated_data)

    class Meta:
        model = models.AnimalGroup
        fields = "__all__"
        extra_kwargs = {
            "name": {"required": True},
            "species": {"required": True},
            "strain": {"required": True},
        }


class EndpointGroupSerializer(serializers.ModelSerializer):
    endpoint = serializers.PrimaryKeyRelatedField(read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["hasVariance"] = instance.hasVariance
        ret["isReported"] = instance.isReported
        return ret

    def validate(self, data):
        if hasattr(self, "initial_data"):
            try:
                endpoint_id = self.initial_data.get("endpoint_id", -1)
                models.Endpoint.objects.get(id=endpoint_id)
                data["endpoint_id"] = endpoint_id
            except ValueError:
                raise serializers.ValidationError("Endpoint ID must be a number.")
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Endpoint ID does not exist.")

        return super().validate(data)

    class Meta:
        model = models.EndpointGroup
        fields = "__all__"


class EndpointSerializer(serializers.ModelSerializer):
    assessment = serializers.PrimaryKeyRelatedField(read_only=True)
    effects = EffectTagsSerializer(read_only=True)
    animal_group = AnimalGroupSerializer(read_only=True, required=False)
    groups = EndpointGroupSerializer(many=True, required=False)

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

    def validate(self, data):
        # Validate animal group
        if "animal_group_id" in self.initial_data:
            # Get animal group instance
            animal_group_id = self.initial_data.get("animal_group_id")
            try:
                animal_group = models.AnimalGroup.objects.get(id=animal_group_id)
                data["animal_group"] = AnimalGroupSerializer(animal_group).data
            except ValueError:
                raise serializers.ValidationError("Animal group ID must be a number.")
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Animal group ID does not exist.")
        elif "animal_group" in self.initial_data:
            animal_group_serializer = AnimalGroupSerializer(
                data=self.initial_data.get("animal_group")
            )
            animal_group_serializer.is_valid(raise_exception=True)
            data["animal_group"] = animal_group_serializer.validated_data
        else:
            # Serializer needs one form of animal group identifier
            raise serializers.ValidationError("Expected 'animal_group' or 'animal_group_id'.")

        data["assessment_id"] = data["animal_group"]["experiment"]["study"]["assessment"]

        return super().validate(data)

    def create(self, validated_data):
        animal_group_id = self.initial_data.get("animal_group_id")
        animal_group = models.AnimalGroup.objects.get(id=animal_group_id)
        if not animal_group.experiment.study.assessment.user_can_edit_object(
            self.context["request"].user
        ):
            raise exceptions.PermissionDenied("Invalid permission to edit assessment.")
        validated_data["animal_group"] = animal_group

        groups = list()
        if "groups" in validated_data:
            validated_data.pop("groups")
        endpoint = models.Endpoint.objects.create(**validated_data)
        groups_data = self.initial_data.get("groups", list())
        for group in groups_data:
            group["endpoint_id"] = endpoint.id
            group_serializer = EndpointGroupSerializer(data=group)
            group_serializer.is_valid(raise_exception=True)
            groups.append(group_serializer)
        # All groups are valid
        for group in groups:
            group.save()
        return endpoint

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
