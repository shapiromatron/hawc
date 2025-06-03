from rest_framework import serializers

from ..assessment.models import DoseUnits, DSSTox, EffectTag, Species, Strain
from ..assessment.serializers import DSSToxSerializer, SpeciesSerializer, StrainSerializer
from ..common.serializers import FlexibleChoiceField, IdLookupMixin
from . import constants, models


class ExperimentSerializer(IdLookupMixin, serializers.ModelSerializer):
    design = FlexibleChoiceField(choices=constants.ExperimentDesign.choices)

    class Meta:
        model = models.Experiment
        fields = "__all__"


class ChemicalSerializer(serializers.ModelSerializer):
    dtxsid_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="dtxsid",
        queryset=DSSTox.objects.all(),
        required=False,
        allow_null=True,
    )
    dtxsid = DSSToxSerializer(read_only=True)

    class Meta:
        model = models.Chemical
        fields = "__all__"


class SimpleAnimalGroupSerializer(serializers.ModelSerializer):
    # Simplified serializer to display Animal Group parents
    class Meta:
        model = models.AnimalGroup
        fields = ("id", "name")


class AnimalGroupSerializer(serializers.ModelSerializer):
    species_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="species",
        queryset=Species.objects.all(),
        required=True,
        allow_null=False,
    )
    species = SpeciesSerializer(read_only=True)

    strain_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="strain",
        queryset=Strain.objects.all(),
        required=True,
        allow_null=False,
    )
    strain = StrainSerializer(read_only=True)

    sex = FlexibleChoiceField(choices=constants.Sex.choices)
    lifestage_at_exposure = FlexibleChoiceField(
        required=False, choices=constants.Lifestage.choices, allow_blank=True
    )
    lifestage_at_assessment = FlexibleChoiceField(
        required=False, choices=constants.Lifestage.choices, allow_blank=True
    )
    generation = FlexibleChoiceField(required=False, choices=constants.Generation.choices)

    parent_ids = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="parents",
        queryset=models.AnimalGroup.objects.all(),
        required=False,
        allow_null=True,
        many=True,
    )
    parents = SimpleAnimalGroupSerializer(required=False, many=True, read_only=True)

    def validate(self, data):
        errors = {}

        if self.instance is None:
            experiment = data.get("experiment")
            species = data.get("species")
            strain = data.get("strain")
            parents = data.get("parents")
        else:
            experiment = data.get("experiment", self.instance.experiment)
            species = data.get("species", self.instance.species)
            strain = data.get("strain", self.instance.strain)
            parents = data.get("parents", self.instance.parents.all())

        if species.id != strain.species_id:
            errors["strain"] = "Strain must be valid for species"

        parent_errors = []
        if "parents" in data and self.instance is not None:
            # ensure they didn't supply the animal-group itself as a parent
            if self.instance.id in [p.id for p in parents]:
                parent_errors.append("Self cannot be parent of self")

        # ensure experiment/parents match
        if parents is not None and len(parents) > 0:
            if any(p.experiment_id != experiment.id for p in parents):
                parent_errors.append(
                    "This animal group's experiment and one or more parent's experiment are mismatched."
                )

        if len(parent_errors) > 0:
            errors["parent_ids"] = parent_errors

        if len(errors.keys()) > 0:
            raise serializers.ValidationError(errors)

        return data

    class Meta:
        model = models.AnimalGroup
        fields = "__all__"


class TreatmentSerializer(serializers.ModelSerializer):
    chemical_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="chemical",
        queryset=models.Chemical.objects.all(),
        required=True,
        allow_null=False,
    )
    chemical = ChemicalSerializer(read_only=True)

    route_of_exposure = FlexibleChoiceField(choices=constants.RouteExposure.choices)

    class Meta:
        model = models.Treatment
        fields = "__all__"


class DoseGroupSerializer(serializers.ModelSerializer):
    dose_units = serializers.SlugRelatedField(
        slug_field="name",
        queryset=DoseUnits.objects.all(),
    )

    class Meta:
        model = models.DoseGroup
        fields = "__all__"


class EndpointSerializer(serializers.ModelSerializer):
    # TODO - implement EHV integration

    additional_tags = serializers.SlugRelatedField(
        slug_field="slug",
        many=True,
        allow_null=True,
        required=False,
        queryset=EffectTag.objects.all(),
    )

    class Meta:
        model = models.Endpoint
        fields = "__all__"


class ObservationTimeSerializer(serializers.ModelSerializer):
    endpoint_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="endpoint",
        queryset=models.Endpoint.objects.all(),
        required=True,
        allow_null=False,
    )
    endpoint = EndpointSerializer(read_only=True)

    observation_time_units = FlexibleChoiceField(choices=constants.ObservationTimeUnits.choices)

    class Meta:
        model = models.ObservationTime
        fields = "__all__"


class DataExtractionSerializer(serializers.ModelSerializer):
    dataset_type = FlexibleChoiceField(choices=constants.DatasetType.choices)
    variance_type = FlexibleChoiceField(
        choices=constants.VarianceType.choices, required=False, allow_blank=True
    )
    method_to_control_for_litter_effects = FlexibleChoiceField(
        choices=constants.MethodToControlForLitterEffects.choices
    )

    def validate(self, attrs):
        errors = []
        if self.instance is None:
            experiment = attrs.get("experiment")
            endpoint = attrs.get("endpoint")
            treatment = attrs.get("treatment")
            observation_timepoint = attrs.get("observation_timepoint")
        else:
            experiment = attrs.get("experiment", self.instance.experiment)
            endpoint = attrs.get("endpoint", self.instance.endpoint)
            treatment = attrs.get("treatment", self.instance.treatment)
            observation_timepoint = attrs.get(
                "observation_timepoint", self.instance.observation_timepoint
            )

        if (
            endpoint.experiment_id != treatment.experiment_id
            or experiment.id != endpoint.experiment_id
        ):
            errors.append("Endpoint/Treatment/Experiment mismatch")

        if endpoint.id != observation_timepoint.endpoint_id:
            errors.append("Observation Time/Endpoint mismatch")

        if errors:
            raise serializers.ValidationError({"general": errors})

        return attrs

    class Meta:
        model = models.DataExtraction
        fields = "__all__"


class DoseResponseGroupLevelDataSerializer(serializers.ModelSerializer):
    treatment_related_effect = FlexibleChoiceField(choices=constants.TreatmentRelatedEffect.choices)

    class Meta:
        model = models.DoseResponseGroupLevelData
        fields = "__all__"


class DoseResponseAnimalLevelDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DoseResponseAnimalLevelData
        fields = "__all__"


class StudyLevelValueSerializer(IdLookupMixin, serializers.ModelSerializer):
    value_type = FlexibleChoiceField(choices=constants.StudyLevelTypeChoices.choices)
    units = serializers.SlugRelatedField(slug_field="name", queryset=DoseUnits.objects.all())

    class Meta:
        model = models.StudyLevelValue
        fields = "__all__"
