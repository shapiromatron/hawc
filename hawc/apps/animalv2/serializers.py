from rest_framework import serializers

from ..assessment.models import DoseUnits, DSSTox, EffectTag, Species, Strain
from ..assessment.serializers import (
    DSSToxSerializer,
    SpeciesSerializer,
    StrainSerializer,
)
from ..common.serializers import FlexibleChoiceField, IdLookupMixin
from ..study.models import Study
from ..study.serializers import StudySerializer
from . import constants, models


class ExperimentSerializer(IdLookupMixin, serializers.ModelSerializer):
    study_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="study",
        queryset=Study.objects.all(),
        required=True,
        allow_null=False,
    )
    study = StudySerializer(read_only=True)
    design = FlexibleChoiceField(choices=constants.ExperimentDesign.choices)

    class Meta:
        model = models.Experiment
        exclude = ["created", "last_updated"]


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
        fields = [
            "id",
            "experiment",
            "name",
            "cas",
            "dtxsid_id",
            "dtxsid",
            "source",
            "purity",
            "vehicle",
            "comments",
        ]


# stripped down serializer for use when displaying an Animal Group's parents
class SimpleAnimalGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AnimalGroup
        fields = ["id", "name"]


class AnimalGroupSerializer(serializers.ModelSerializer):
    # TODO: support on-the-fly species/strain creation

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

        # check either the PATCH/PUT/POST payload if they supplied
        # strain/species, or loook on the existing object. At
        # the end of the day, they need to match.
        species_src = "supplied" if "species" in data else "preexisting"
        strain_src = "supplied" if "strain" in data else "preexisting"

        # give a hopefully helpful error message for the problematic field
        if species.id != strain.species.id:
            if species_src == "supplied" and strain_src == "supplied":
                error_field = "strain"
                error_msg = "Strain must be of the same species as the supplied species."
            elif species_src == "supplied":
                error_field = "species"
                error_msg = (
                    "Species was supplied but existing strain was not (and would be invalid)."
                )
            elif strain_src == "supplied":
                error_field = "strain"
                error_msg = "Supplied strain is invalid for existing species."

            errors[error_field] = error_msg

        parent_errors = []
        if "parents" in data and self.instance is not None:
            # ensure they didn't supply the animal-group itself as a parent
            parent_ids = [p.id for p in parents]
            if self.instance.id in parent_ids:
                # errors["parent_ids"] = "circular reference"
                parent_errors.append("circular reference")

        # ensure experiment/parents match
        if parents is not None:
            if any([p.experiment_id != experiment.id for p in parents]):
                parent_errors.append(
                    "this animal group's experiment and one or more parent's experiment are mismatched."
                )

        if len(parent_errors) > 0:
            errors["parent_ids"] = parent_errors

        if len(errors.keys()) > 0:
            raise serializers.ValidationError(errors)

        return data

    class Meta:
        model = models.AnimalGroup
        exclude = ["created", "last_updated"]


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
        exclude = ["created", "last_updated"]


class DoseGroupSerializer(serializers.ModelSerializer):
    treatment_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="treatment",
        queryset=models.Treatment.objects.all(),
        required=True,
        allow_null=False,
    )
    treatment = TreatmentSerializer(read_only=True)

    dose_units = serializers.SlugRelatedField(
        slug_field="name",
        queryset=DoseUnits.objects.all(),
    )

    class Meta:
        model = models.DoseGroup
        exclude = ["created", "last_updated"]


class EndpointSerializer(serializers.ModelSerializer):
    # TODO: name, system, organ, effect, effect-subtype have EHV-related _term fields in the db; these are not
    # currently implemented in either the UI or the API.

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
        exclude = ["created", "last_updated"]


class DataExtractionSerializer(serializers.ModelSerializer):
    endpoint_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="endpoint",
        queryset=models.Endpoint.objects.all(),
        required=True,
        allow_null=False,
    )
    endpoint = EndpointSerializer(read_only=True)

    treatment_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="treatment",
        queryset=models.Treatment.objects.all(),
        required=True,
        allow_null=False,
    )
    treatment = TreatmentSerializer(read_only=True)

    observation_timepoint_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="observation_timepoint",
        queryset=models.ObservationTime.objects.all(),
        required=True,
        allow_null=False,
    )
    observation_timepoint = ObservationTimeSerializer(read_only=True)

    dataset_type = FlexibleChoiceField(choices=constants.DatasetType.choices)
    variance_type = FlexibleChoiceField(
        choices=constants.VarianceType.choices, required=False, allow_blank=True
    )
    method_to_control_for_litter_effects = FlexibleChoiceField(
        choices=constants.MethodToControlForLitterEffects.choices
    )

    def validate(self, data):
        # check that endpoint/treatment are part of same experiment (and match the experiment associated
        # with the data extraction), and that obstime is part of the same endpoint as the associated one

        errors = []
        if self.instance is None:
            experiment = data.get("experiment")
            endpoint = data.get("endpoint")
            treatment = data.get("treatment")
            observation_timepoint = data.get("observation_timepoint")
        else:
            experiment = data.get("experiment", self.instance.experiment)
            endpoint = data.get("endpoint", self.instance.endpoint)
            treatment = data.get("treatment", self.instance.treatment)
            observation_timepoint = data.get(
                "observation_timepoint", self.instance.observation_timepoint
            )

        if (
            endpoint.experiment.id != treatment.experiment.id
            or experiment.id != endpoint.experiment.id
        ):
            errors.append("Endpoint/Treatment/Experiment mismatch")

        if endpoint.id != observation_timepoint.endpoint.id:
            errors.append("Observation Time/Endpoint mismatch")

        if len(errors) > 0:
            raise serializers.ValidationError({"general": errors})

        return data

    class Meta:
        model = models.DataExtraction
        exclude = ["created", "last_updated"]


class DoseResponseGroupLevelDataSerializer(serializers.ModelSerializer):
    data_extraction_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="data_extraction",
        queryset=models.DataExtraction.objects.all(),
        required=True,
        allow_null=False,
    )
    data_extraction = DataExtractionSerializer(read_only=True)

    treatment_related_effect = FlexibleChoiceField(choices=constants.TreatmentRelatedEffect.choices)

    class Meta:
        model = models.DoseResponseGroupLevelData
        exclude = ["created", "last_updated"]


class DoseResponseAnimalLevelDataSerializer(serializers.ModelSerializer):
    data_extraction_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="data_extraction",
        queryset=models.DataExtraction.objects.all(),
        required=True,
        allow_null=False,
    )
    data_extraction = DataExtractionSerializer(read_only=True)

    class Meta:
        model = models.DoseResponseAnimalLevelData
        exclude = ["created", "last_updated"]


class StudyLevelValueSerializer(IdLookupMixin, serializers.ModelSerializer):
    study_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="study",
        queryset=Study.objects.all(),
        required=True,
        allow_null=False,
    )
    study = StudySerializer(read_only=True)

    value_type = FlexibleChoiceField(choices=constants.StudyLevelTypeChoices.choices)

    units = serializers.SlugRelatedField(
        slug_field="name",
        queryset=DoseUnits.objects.all(),
    )

    class Meta:
        model = models.StudyLevelValue
        exclude = ["created", "last_updated"]
