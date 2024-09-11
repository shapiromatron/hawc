import json

import pandas as pd
from rest_framework import serializers

from ...tools.tables.set.constants import DataSourceChoices
from ..animal import models as animal_models
from ..assessment.models import Assessment
from ..common.helper import int_or_float
from ..common.serializers import FlexibleFieldsMixin
from ..materialized.models import FinalRiskOfBiasScore
from ..study.models import Study
from . import constants


class SummaryTableDataSerializer(serializers.Serializer):
    table_type = serializers.ChoiceField(constants.TableType.choices)

    @property
    def cache_key(self):
        return (
            f"table-type-{self.validated_data['table_type']}-{self.validated_data['ser'].cache_key}"
        )

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


class StudySerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = ["id", "short_citation"]
        read_only_fields = fields


class ExperimentSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = animal_models.Experiment
        fields = ["id", "study_id", "name", "chemical"]
        read_only_fields = fields


class AnimalGroupSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    route_of_exposure = serializers.SerializerMethodField()
    treatment_period = serializers.SerializerMethodField()
    doses = serializers.SerializerMethodField()

    class Meta:
        model = animal_models.AnimalGroup
        fields = [
            "id",
            "experiment_id",
            "name",
            "description",
            "route_of_exposure",
            "treatment_period",
            "doses",
        ]
        read_only_fields = fields

    def get_description(self, obj):
        return f"{obj.generation}{' ' if obj.generation else ''}{obj.species.name}, {obj.strain.name} ({obj.sex_symbol})"

    def get_route_of_exposure(self, obj):
        return obj.dosing_regime.get_route_of_exposure_display()

    def get_treatment_period(self, obj):
        text = obj.experiment.get_type_display()
        if "(" in text:
            text = text[: text.find("(")]
        if obj.dosing_regime.duration_exposure_text:
            text = f"{text} ({obj.dosing_regime.duration_exposure_text})"
        return text

    def get_doses(self, obj):
        dose_dict = dict()
        dgs = obj.dosing_regime.doses.all()
        for dg in dgs:
            if dg.dose_units.name not in dose_dict:
                dose_dict[dg.dose_units.name] = str(int_or_float(dg.dose))
            else:
                dose_dict[dg.dose_units.name] += f", {int_or_float(dg.dose)}"
        return dose_dict


class EndpointSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = animal_models.Endpoint
        fields = ["id", "animal_group_id", "name", "system", "effect"]
        read_only_fields = fields


class StudyEvaluationSerializer(serializers.Serializer):
    assessment_id = serializers.PrimaryKeyRelatedField(queryset=Assessment.objects.all())
    data_source = serializers.ChoiceField(
        choices=[DataSourceChoices.Study.value, DataSourceChoices.Animal.value]
    )
    published_only = serializers.BooleanField()

    def validate(self, data):
        # Check permissions for non published data
        if (
            "request" in self.context
            and data["published_only"] is False
            and data["assessment_id"].user_is_reviewer_or_higher(self.context["request"].user)
            is False
        ):
            raise serializers.ValidationError(
                {"published_only": "Must be part of team to view unpublished data."}
            )
        data["data_source"] = DataSourceChoices(data["data_source"])
        return data

    @property
    def cache_key(self):
        return f"data-source-{self.validated_data['data_source']}-published-only-{self.validated_data['published_only']}"

    @property
    def _custom_fields(self):
        # fields that use custom aggregation
        if self.validated_data["data_source"] == DataSourceChoices.Animal:
            return ["animal_group_doses"]

    @property
    def _id_fields(self):
        # id fields, in order of specificity
        if self.validated_data["data_source"] == DataSourceChoices.Animal:
            return ["study_id", "experiment_id", "animal_group_id", "endpoint_id"]

    @property
    def _study_filters(self):
        # filter from assessment
        study_filters = {"assessment_id": self.validated_data["assessment_id"]}
        # filter from data_source
        if self.validated_data["data_source"] == DataSourceChoices.Animal:
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
        return study_df.convert_dtypes()

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
        animal_group_qs = (
            animal_models.AnimalGroup.objects.filter(
                experiment_id__in=experiment_df["experiment_id"].values
            )
            .select_related("species", "strain", "dosing_regime", "experiment")
            .prefetch_related("dosing_regime__doses", "dosing_regime__doses__dose_units")
        )
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
        ]
        # combine grouped dfs
        final_df = pd.concat(group_dfs, ignore_index=True)
        # return df
        return final_df.convert_dtypes()

    def _aggregate_custom(self, series):
        if series.name == "animal_group_doses":
            aggregated_dict = dict()
            for dose_dict in series.dropna():
                for key, value in dose_dict.items():
                    if key not in aggregated_dict:
                        aggregated_dict[key] = set()
                    aggregated_dict[key].add(value)
            return aggregated_dict

    def _aggregate(self, series):
        if series.empty:
            # special case for empty dataset
            return
        if series.name in self._custom_fields:
            # run any custom aggregations
            return self._aggregate_custom(series)
        if series.name in self._id_fields:
            # use the first occurence; id fields are handled after aggregation
            return series.iloc[0]
        # run default aggregation
        return "; ".join([str(_) for _ in series.dropna().sort_values().unique()])

    def _group_df(self, df, model):
        # aggregate
        column = f"{model}_id"
        groups = df.groupby(column, as_index=False)
        df = groups.agg(self._aggregate)
        # add identifying columns
        df.insert(0, "type", model)
        df.insert(1, "id", df[column])
        # drop irrelevant id fields
        return df.drop(columns=self._id_fields[self._id_fields.index(column) + 1 :])

    def _get_rob_df(self):
        fields = [
            "study_id",
            "metric_id",
            "score_id",
            "score_label",
            "score_notes",
            "score_score",
            "bias_direction",
            "is_default",
            "riskofbias_id",
            "content_type_id",
            "object_id",
        ]
        study_ids = Study.objects.filter(**self._study_filters).values_list("id", flat=True)
        rob_values = (
            FinalRiskOfBiasScore.objects.filter(study_id__in=study_ids)
            .order_by("score_id")
            .values_list(*fields)
        )
        return pd.DataFrame(rob_values, columns=fields).convert_dtypes()

    def _get_df(self):
        data_source = self.validated_data["data_source"]
        if data_source == DataSourceChoices.Study:
            return self._get_study_df()
        if data_source == DataSourceChoices.Animal:
            return self._get_ani_df()

    def get_dfs(self):
        return {"data": self._get_df(), "rob": self._get_rob_df()}

    def get_data(self):
        # load DataFrame's json dump to work around pd.NA being non-JSON serializable
        return {key: json.loads(df.to_json(orient="records")) for key, df in self.get_dfs().items()}
