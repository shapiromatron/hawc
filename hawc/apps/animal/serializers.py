import itertools
import json

from django.db import transaction
from rest_framework import serializers

from ..assessment.api import user_can_edit_object
from ..assessment.models import DoseUnits, DSSTox
from ..assessment.serializers import DSSToxSerializer, EffectTagsSerializer
from ..common.api import DynamicFieldsMixin
from ..common.helper import SerializerHelper
from ..common.serializers import get_matching_instance, get_matching_instances
from ..study.models import Study
from ..study.serializers import StudySerializer
from ..vocab.constants import VocabularyTermType
from . import forms, models


class ExperimentSerializer(serializers.ModelSerializer):
    study = StudySerializer(required=False, read_only=True)
    dtxsid = DSSToxSerializer(required=False, read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["url"] = instance.get_absolute_url()
        ret["type"] = instance.get_type_display()
        ret["is_generational"] = instance.is_generational()
        return ret

    def validate(self, data):
        # Validate parent object
        self.study = get_matching_instance(Study, self.initial_data, "study_id")
        user_can_edit_object(self.study, self.context["request"].user, raise_exception=True)

        # add additional checks from forms.ExperimentForm
        form = forms.ExperimentForm(data=data, parent=self.study)
        if form.is_valid() is False:
            raise serializers.ValidationError(form.errors)

        # validate dtxsid
        dtxsid = self.initial_data.get("dtxsid")
        if dtxsid:
            try:
                data["dtxsid"] = DSSTox.objects.get(pk=dtxsid)
            except models.ObjectDoesNotExist:
                raise serializers.ValidationError(dict(dtxsid=f"DSSTox {dtxsid} does not exist"))

        return data

    def create(self, validated_data):
        return models.Experiment.objects.create(**validated_data, study=self.study)

    class Meta:
        model = models.Experiment
        fields = "__all__"


class DosesSerializer(serializers.ModelSerializer):
    dose_regime = serializers.PrimaryKeyRelatedField(read_only=True)
    dose_units_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="dose_units",
        queryset=DoseUnits.objects.all(),
        required=True,
        allow_null=False,
    )

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
        fields = ("id", "name")


class DosingRegimeSerializer(serializers.ModelSerializer):
    doses = DosesSerializer(many=True)
    dosed_animals = AnimalGroupRelationSerializer(required=False)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["route_of_exposure"] = instance.get_route_of_exposure_display()
        ret["positive_control"] = instance.get_positive_control_display()
        ret["negative_control"] = instance.get_negative_control_display()
        return ret

    def validate(self, data):
        # validate dose-groups too
        dose_serializers = []
        doses = self.initial_data.get("doses", [])
        for dose in doses:
            dose_serializer = DosesSerializer(data=dose)
            dose_serializer.is_valid(raise_exception=True)
            dose_serializers.append(dose_serializer)
        self.dose_serializers = dose_serializers

        # validate that we have the same number of `dose_group_id`
        dose_groups = set([d["dose_group_id"] for d in doses])
        units = set([d["dose_units_id"] for d in doses])

        if len(dose_groups) == 0:
            raise serializers.ValidationError("Must have at least one dose-group.")

        expected_dose_groups = list(range(max(dose_groups) + 1))
        if dose_groups != set(expected_dose_groups):
            raise serializers.ValidationError(f"Expected `dose_group_id` in {expected_dose_groups}")

        expected_doses = len(dose_groups) * len(units)
        if len(doses) != expected_doses:
            raise serializers.ValidationError(f"Expected {expected_doses} dose-groups.")

        expected_set = set(itertools.product(dose_groups, units))
        actual_set = set((d["dose_group_id"], d["dose_units_id"]) for d in doses)
        if expected_set != actual_set:
            raise serializers.ValidationError("Missing or duplicate dose-groups")

        data["num_dose_groups"] = len(dose_groups)

        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("doses", None)
        dosing_regime = models.DosingRegime.objects.create(**validated_data)
        for dose_serializer in self.dose_serializers:
            dose_serializer.save(dose_regime_id=dosing_regime.id)
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
        # Validate parent object
        experiment = get_matching_instance(models.Experiment, self.initial_data, "experiment_id")
        user_can_edit_object(experiment, self.context["request"].user, raise_exception=True)
        data["experiment"] = experiment

        # check dosing_regime
        dosing_regime = get_matching_instance(
            models.DosingRegime, self.initial_data, "dosing_regime_id"
        )
        if (
            dosing_regime.dosed_animals
            and dosing_regime.dosed_animals.experiment_id != experiment.id
        ):
            raise serializers.ValidationError("Dosed animals must be from the same experiment.")
        data["dosing_regime"] = dosing_regime

        # set siblings (optional)
        if "siblings_id" in self.initial_data:
            siblings = get_matching_instance(models.AnimalGroup, self.initial_data, "siblings_id")
            if siblings.experiment_id != experiment.id:
                raise serializers.ValidationError(
                    {"siblings_id": "Sibling must be in same experiment"}
                )
            data["siblings"] = siblings

        # set parents (optional)
        if "parent_ids" in self.initial_data:
            parents = get_matching_instances(models.AnimalGroup, self.initial_data, "parent_ids")
            if any([parent.experiment_id != experiment.id for parent in parents]):
                raise serializers.ValidationError(
                    {"parent_ids": "Parent must be in same experiment"}
                )
            data["parents"] = parents

        # add form checks - this should be identical to forms.AnimalGroup.clean - DRY?
        species = data.get("species", None)
        strain = data.get("strain", None)
        if strain and species and species != strain.species:
            raise serializers.ValidationError({"strain": forms.AnimalGroupForm.STRAIN_NOT_SPECIES})

        return data

    @transaction.atomic
    def create(self, validated_data):
        parents = validated_data.pop("parents", None)
        instance = models.AnimalGroup.objects.create(**validated_data)
        if parents:
            instance.parents.set(parents)
        return instance

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
        ret["treatment_effect"] = instance.get_treatment_effect_display()
        return ret

    def validate(self, data):
        errors = forms.EndpointGroupForm.clean_endpoint_group(
            self.context["endpoint_data"].get("data_type", "C"),
            self.context["endpoint_data"].get("variance_type", 0),
            data,
        )
        if errors:
            err = {k: [v] for k, v in errors.items()}
            raise serializers.ValidationError(err)

        return data

    class Meta:
        model = models.EndpointGroup
        fields = "__all__"


class EndpointSerializer(serializers.ModelSerializer):
    assessment = serializers.PrimaryKeyRelatedField(read_only=True)
    effects = EffectTagsSerializer(read_only=True)
    animal_group = AnimalGroupSerializer(read_only=True, required=False)
    groups = EndpointGroupSerializer(many=True, required=False)
    name = serializers.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" in kwargs:
            self.fields["groups"].context.update(endpoint_data=kwargs["data"])

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

        ret["bmds"] = [
            session.get_selected_model() for session in instance.bmd_sessions.filter(active=True)
        ]

        return ret

    def _validate_term_and_text(self, data, term_field: str, text_field: str, term_type_str: str):
        """
        Validate logic for both term field and the text field
        """

        term = data.get(term_field)
        if term is None:
            return

        # Term namespace must match assessment
        if self.assessment.vocabulary != term.namespace:
            raise serializers.ValidationError(
                {
                    term: f"Assessment vocabulary ({self.assessment.vocabulary}) does not match term namespace ({term.namespace})."
                }
            )

        # Term type must field type
        term_type = getattr(VocabularyTermType, term_type_str)
        if term.type != term_type:
            raise serializers.ValidationError(
                {term_field: f"Got term type '{term.type}', expected type '{term_type}'."}
            )

        # Save the non-term equivalent
        data[text_field] = term.name

    def validate(self, data):
        # name or name_term must be given
        if data.get("name") is None and data.get("name_term") is None:
            raise serializers.ValidationError({"name": ["'name' or 'name_term' is required."]})

        # Validate parent object
        self.animal_group = get_matching_instance(
            models.AnimalGroup, self.initial_data, "animal_group_id"
        )
        user_can_edit_object(self.animal_group, self.context["request"].user, raise_exception=True)
        self.assessment = self.animal_group.get_assessment()
        data["animal_group_id"] = self.animal_group.id
        data["assessment_id"] = self.assessment.id

        # validate terms and text
        self._validate_term_and_text(data, "system_term", "system", "system")
        self._validate_term_and_text(data, "organ_term", "organ", "organ")
        self._validate_term_and_text(data, "effect_term", "effect", "effect")
        self._validate_term_and_text(
            data, "effect_subtype_term", "effect_subtype", "effect_subtype"
        )
        self._validate_term_and_text(data, "name_term", "name", "endpoint_name")

        # set animal_group on instance for cleaning rules
        instance = models.Endpoint(animal_group=self.animal_group)
        errors = forms.EndpointForm.clean_endpoint(instance, data)
        if errors:
            err = {k: [v] for k, v in errors.items()}
            raise serializers.ValidationError(err)

        # validate all groups
        groups = self.initial_data.get("groups", [])
        if groups:
            num_dose_groups = self.animal_group.dosing_regime.num_dose_groups
            valid_ids = set(range(num_dose_groups))
            if len(groups) != num_dose_groups:
                raise serializers.ValidationError(
                    f"If entering groups, all {num_dose_groups} must be entered"
                )
            if valid_ids != set([g.get("dose_group_id", -1) for g in groups]):
                raise serializers.ValidationError(
                    f"For groups, `dose_group_id` must include all values in {list(valid_ids)}"
                )
            for fld in ("NOEL", "LOEL", "FEL"):
                val = data.get(fld, -999)
                if val != -999 and val not in valid_ids:
                    raise serializers.ValidationError(f"{fld} must be -999 or in {list(valid_ids)}")

        # validate individual groups
        group_serializers = []
        for group in groups:
            group_serializer = EndpointGroupSerializer(
                data=group, context=self.fields["groups"].context
            )
            group_serializer.is_valid(raise_exception=True)
            group_serializers.append(group_serializer)
        self.group_serializers = group_serializers

        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("groups", None)
        endpoint = models.Endpoint.objects.create(**validated_data)
        for group_serializer in self.group_serializers:
            group_serializer.save(endpoint_id=endpoint.id)
        return endpoint

    class Meta:
        model = models.Endpoint
        fields = "__all__"


class ExperimentCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Experiment
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = (*cleanup_fields, "id")

    def get_study_short_citation(self, obj):
        return obj.study.short_citation


class AnimalGroupCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.AnimalGroup
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = (*cleanup_fields, "id")

    def get_study_short_citation(self, obj):
        return obj.experiment.study.short_citation


class EndpointCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Endpoint
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = (*cleanup_fields, "id", *tuple(model.TERM_FIELD_MAPPING.values()))

    def get_study_short_citation(self, obj):
        return obj.animal_group.experiment.study.short_citation


class DosingRegimeCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.DosingRegime
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = (*cleanup_fields, "id")

    def get_study_short_citation(self, obj):
        return obj.dosed_animals.experiment.study.short_citation


SerializerHelper.add_serializer(models.AnimalGroup, AnimalGroupSerializer)
SerializerHelper.add_serializer(models.Endpoint, EndpointSerializer)
