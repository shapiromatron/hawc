import pandas as pd
from rest_framework import serializers

from ..animal import models as animal_models
from ..assessment.models import Assessment
from ..materialized.models import FinalRiskOfBiasScore
from ..study.models import Study
from . import constants


class SummaryTableDataSerializer(serializers.Serializer):
    table_type = serializers.ChoiceField(constants.TableType.choices)

    def validate(self, data):
        if data["table_type"] == constants.TableType.STUDY_EVALUATION:
            ser = StudyEvaluationSerializer(data=self.initial_data, context=self.context)
            ser.is_valid(raise_exception=True)
            data["ser"] = ser
        return data

    def get_data(self):
        ser = self.validated_data.get("ser")
        if ser is not None:
            return ser.get_data()


class FlexibleFieldsMixin:
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        field_prefix = kwargs.pop("field_prefix", "")
        field_renames = kwargs.pop("field_renames", {})

        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        # TODO validate prefix and renames to make sure theres no clashes with other fields

        if not field_prefix and not field_renames:
            # If nothing else needs to be done, return
            return

        # 'fields' is a BindingDict, which has an underlying OrderedDict.
        # any changes require it to be rebuilt to maintain its order.
        for field_name in list(self.fields):
            if field_name in field_renames:
                # handle renames
                new_field_name = field_renames[field_name]
                if field_name == new_field_name:
                    # special case; assign on the underlying OrderedDict to avoid error on BindingDict __setitem__
                    self.fields.fields[field_name] = self.fields.pop(field_name)
                else:
                    self.fields[new_field_name] = self.fields.pop(field_name)
            elif field_prefix:
                # handle prefixes
                self.fields[field_prefix + field_name] = self.fields.pop(field_name)
            else:
                # handle case of no rename or prefix
                self.fields.fields[field_name] = self.fields.pop(field_name)


class StudySerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = ["id", "short_citation"]
        read_only_fields = fields


class ExperimentSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = animal_models.Experiment
        fields = ["id", "study_id"]
        read_only_fields = fields


class AnimalGroupSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = animal_models.AnimalGroup
        fields = ["id", "experiment_id", "description"]
        read_only_fields = fields

    def get_description(self, obj):
        return f"{obj.generation}{' ' if obj.generation else ''}{obj.species.name}, {obj.strain.name} ({obj.sex_symbol})"


class EndpointSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = animal_models.Endpoint
        fields = ["id", "animal_group_id"]
        read_only_fields = fields


class StudyEvaluationSerializer(serializers.Serializer):
    assessment_id = serializers.PrimaryKeyRelatedField(queryset=Assessment.objects.all())
    data_source = serializers.ChoiceField(choices=["study", "ani"])
    published_only = serializers.BooleanField()

    def validate(self, data):
        # Check permissions for non published data
        if (
            data["published_only"] is False
            and data["assessment_id"].user_is_part_of_team(self.context["request"].user) is False
        ):
            raise serializers.ValidationError("Must be part of team to view unpublished data.")
        return data

    @property
    def _id_fields(self):
        if self.validated_data["data_source"] == "ani":
            return ["study_id", "experiment_id", "animal_group_id", "endpoint_id"]

    @property
    def _study_filters(self):
        # filter from assessment
        study_filters = {"assessment_id": self.validated_data["assessment_id"]}
        # filter from data_source
        if self.validated_data["data_source"] == "ani":
            study_filters["bioassay"] = True
        # filter from published_only
        if self.validated_data["published_only"]:
            study_filters["published"] = True
        return study_filters

    def _get_study_df(self):
        # get queryset
        study_qs = Study.objects.filter(**self._study_filters)
        # serialize queryset
        study_ser = StudySerializer(study_qs, many=True, field_prefix="study_")
        # create df
        study_df = pd.DataFrame.from_records(study_ser.data, columns=study_ser.child.fields.keys())
        study_df.insert(0, "type", "study")
        study_df.insert(1, "id", study_df["study_id"])
        return study_df.convert_dtypes().replace({pd.NA: None})

    def _get_ani_df(self):
        # get study df
        study_qs = Study.objects.filter(**self._study_filters)
        study_ser = StudySerializer(study_qs, many=True, field_prefix="study_")
        study_df = pd.DataFrame.from_records(study_ser.data, columns=study_ser.child.fields.keys())
        # get experiment df
        experiment_qs = animal_models.Experiment.objects.filter(
            study_id__in=study_df["study_id"].values
        )
        experiment_ser = ExperimentSerializer(
            experiment_qs,
            many=True,
            field_prefix="experiment_",
            field_renames={"study_id": "study_id"},
        )
        experiment_df = pd.DataFrame.from_records(
            experiment_ser.data, columns=experiment_ser.child.fields.keys()
        )
        # get animal group df
        animal_group_qs = animal_models.AnimalGroup.objects.filter(
            experiment_id__in=experiment_df["experiment_id"].values
        ).select_related("species", "strain")
        animal_group_ser = AnimalGroupSerializer(
            animal_group_qs,
            many=True,
            field_prefix="animal_group_",
            field_renames={"experiment_id": "experiment_id"},
        )
        animal_group_df = pd.DataFrame.from_records(
            animal_group_ser.data, columns=animal_group_ser.child.fields.keys()
        )
        # get endpoint df
        endpoint_qs = animal_models.Endpoint.objects.filter(
            animal_group_id__in=animal_group_df["animal_group_id"].values
        )
        endpoint_ser = EndpointSerializer(
            endpoint_qs,
            many=True,
            field_prefix="endpoint_",
            field_renames={"animal_group_id": "animal_group_id"},
        )
        endpoint_df = pd.DataFrame.from_records(
            endpoint_ser.data, columns=endpoint_ser.child.fields.keys()
        )
        # join dfs
        merged_df = (
            study_df.merge(experiment_df, how="left", on="study_id")
            .merge(animal_group_df, how="left", on="experiment_id")
            .merge(endpoint_df, how="left", on="animal_group_id")
        )
        # group dfs by type
        group_dfs = [
            self._group_df(merged_df, "study"),
            self._group_df(merged_df, "experiment"),
            self._group_df(merged_df, "animal_group"),
            self._group_df(merged_df, "endpoint"),
        ]
        # combine grouped dfs
        final_df = pd.concat(group_dfs, ignore_index=True)
        return final_df.convert_dtypes().replace({pd.NA: None})

    def _foo(self, series: pd.Series):
        # TODO rename appropriately
        return "; ".join([str(_) for _ in series.dropna().sort_values().unique()])

    def _aggregate_df(self, df):
        base = df.iloc[0]

        # ids are not aggregated
        df = df.drop(columns=self._id_fields)

        series = df.apply(self._foo, axis=0)
        base.update(series)
        return base

    def _group_df(self, df, model):
        ## aggregate
        column = f"{model}_id"
        df = df.groupby(column, as_index=False).apply(self._aggregate_df)
        ## add identifying columns
        df.insert(0, "type", model)
        df.insert(1, "id", df[column])
        return df.drop(columns=self._id_fields[self._id_fields.index(column) + 1 :])

    def _get_rob_df(self):
        study_ids = Study.objects.filter(**self._study_filters).values_list("id", flat=True)
        rob_values = FinalRiskOfBiasScore.objects.filter(study_id__in=study_ids).values()
        df = pd.DataFrame(
            rob_values,
            columns=[
                "study_id",
                "metric_id",
                "id",
                "score_id",
                "score_label",
                "score_notes",
                "score_score",
                "bias_direction",
                "is_default",
                "riskofbias_id",
                "content_type_id",
                "object_id",
            ],
        )
        return df.convert_dtypes().replace({pd.NA: None})

    def _get_df(self):
        data_source = self.validated_data["data_source"]
        if data_source == "study":
            return self._get_study_df()
        if data_source == "ani":
            return self._get_ani_df()

    def get_dfs(self):
        return {"data": self._get_df(), "rob": self._get_rob_df()}

    def get_data(self):
        return {key: df.to_dict(orient="records") for key, df in self.get_dfs().items()}
