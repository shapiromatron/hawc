import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from plotly.subplots import make_subplots
from rest_framework import serializers

from hawc.services.epa.dsstox import DssSubstance

from ..common.serializers import FlexibleChoiceField
from ..study.models import Study
from . import constants, models


class DSSToxSerializer(serializers.ModelSerializer):
    dashboard_url = serializers.URLField(source="get_dashboard_url", read_only=True)
    img_url = serializers.URLField(source="get_img_url", read_only=True)

    class Meta:
        model = models.DSSTox
        fields = "__all__"
        read_only_fields = ["content"]

    def create(self, validated_data):
        substance = DssSubstance.create_from_dtxsid(validated_data["dtxsid"])
        return models.DSSTox.objects.create(dtxsid=substance.dtxsid, content=substance.content)


class AssessmentSerializer(serializers.ModelSerializer):
    rob_name = serializers.CharField(source="get_rob_name_display", read_only=True)
    dtxsids = DSSToxSerializer(many=True, read_only=True)
    dtxsids_ids = serializers.PrimaryKeyRelatedField(
        write_only=True,
        many=True,
        source="dtxsids",
        queryset=models.DSSTox.objects.all(),
        required=False,
        allow_null=True,
    )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["url"] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.Assessment
        exclude = ("admin_notes",)


class AssessmentMiniSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url")

    class Meta:
        model = models.Assessment
        fields = ("id", "url", "enable_risk_of_bias", "name")


class AssessmentDetailSerializer(serializers.ModelSerializer):
    assessment_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="assessment",
        queryset=models.Assessment.objects.all(),
        required=True,
        allow_null=False,
    )
    assessment = AssessmentMiniSerializer(read_only=True)
    project_status = FlexibleChoiceField(choices=constants.Status.choices)
    peer_review_status = FlexibleChoiceField(choices=constants.PeerReviewType.choices)

    class Meta:
        model = models.AssessmentDetail
        exclude = ("created", "last_updated")


class AssessmentValueSerializer(serializers.ModelSerializer):
    assessment_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="assessment",
        queryset=models.Assessment.objects.all(),
        required=True,
        allow_null=False,
    )
    assessment = AssessmentMiniSerializer(read_only=True)
    study_id = serializers.PrimaryKeyRelatedField(
        source="study",
        queryset=Study.objects.all(),
        required=False,
        allow_null=True,
    )
    evaluation_type = FlexibleChoiceField(choices=constants.EvaluationType.choices)
    value_type = FlexibleChoiceField(choices=constants.ValueType.choices)
    uncertainty = FlexibleChoiceField(choices=constants.UncertaintyChoices.choices)

    class Meta:
        model = models.AssessmentValue
        exclude = ("created", "last_updated")


class EffectTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EffectTag
        fields = ["name", "slug"]


class RelatedEffectTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EffectTag
        fields = ["name", "slug"]

    def to_internal_value(self, data):
        if not isinstance(data, str):
            raise serializers.ValidationError(f"'{data}' must be a string.")
        try:
            return models.EffectTag.objects.get(name=data)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f"'{data}' not found.")


class DoseUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DoseUnits
        fields = "__all__"


class GrowthPlotSerializer(serializers.Serializer):
    model = serializers.ChoiceField(choices=["user", "assessment", "study"])
    grouper = serializers.ChoiceField(choices=["A", "Q", "M"])

    group_mapping = dict(A="Annual", Q="Quarterly", M="Monthly")

    def _build_change_plots(self, df: pd.DataFrame, grouper: str, y_axis: str) -> go.Figure:
        df1 = df.set_index("date").groupby(pd.Grouper(freq=grouper)).count().cumsum().reset_index()
        df2 = (
            df.set_index("date")
            .groupby(pd.Grouper(freq=grouper))
            .count()
            .cumsum()
            .diff(periods=1)
            .dropna()
            .reset_index()
        )

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            subplot_titles=(
                f"Cumulative growth of {y_axis.lower()}",
                f"{self.group_mapping[grouper]} growth of {y_axis.lower()}",
            ),
        )
        fig.update_layout(height=600)

        ax1 = px.bar(df1, x="date", y="id")
        for trace in ax1.data:
            fig.add_trace(trace, row=1, col=1)
        fig.update_yaxes(title_text=y_axis, row=1, col=1)

        ax2 = px.bar(df2, x="date", y="id")
        for trace in ax2.data:
            fig.add_trace(trace, row=2, col=1)
        fig.update_yaxes(title_text=y_axis, row=2, col=1)

        return fig

    def create_figure(self) -> go.Figure:
        model = self.validated_data["model"]
        if model == "user":
            fields = ("id", "date_joined")
            data = list(apps.get_model("myuser", "HAWCUser").objects.values_list(*fields))
            df = pd.DataFrame(data, columns=fields).rename(columns=dict(date_joined="date"))
            fig = self._build_change_plots(df, self.validated_data["grouper"], "New users")
        elif model == "assessment":
            fields = ("id", "created")
            data = list(apps.get_model("assessment", "Assessment").objects.values_list(*fields))
            df = pd.DataFrame(data, columns=fields).rename(columns=dict(created="date"))
            fig = self._build_change_plots(df, self.validated_data["grouper"], "Assessments")
        elif model == "study":
            fields = ("id", "created")
            data = list(apps.get_model("study", "Study").objects.values_list(*fields))
            df = pd.DataFrame(data, columns=fields).rename(columns=dict(created="date"))
            fig = self._build_change_plots(df, self.validated_data["grouper"], "Studies")
        else:
            raise Exception("Unreachable code.")

        return fig


class DatasetRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DatasetRevision
        exclude = ("data",)


class DatasetSerializer(serializers.ModelSerializer):
    absolute_url = serializers.URLField(source="get_absolute_url")
    api_detail_url = serializers.URLField(source="get_api_detail_url")
    api_data_url = serializers.URLField(source="get_api_data_url")
    latest_revision = DatasetRevisionSerializer(many=False, source="get_latest_revision")

    class Meta:
        model = models.Dataset
        fields = "__all__"


class StrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Strain
        fields = "__all__"
