import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.apps import apps
from plotly.subplots import make_subplots
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from . import models


class DSSToxSerializer(serializers.ModelSerializer):
    dashboard_url = serializers.URLField(source="get_dashboard_url")
    img_url = serializers.URLField(source="get_img_url")

    class Meta:
        model = models.DSSTox
        fields = "__all__"


class AssessmentSerializer(serializers.ModelSerializer):
    rob_name = serializers.CharField(source="get_rob_name_display")
    dtxsids = DSSToxSerializer(many=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["url"] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.Assessment
        fields = "__all__"


class AssessmentMiniSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url")

    class Meta:
        model = models.Assessment
        fields = ("id", "url", "enable_risk_of_bias", "name")


class EffectTagsSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        raise ParseError("Not implemented!")

    def to_representation(self, obj):
        # obj is a model-manager in this case; convert to list to serialize
        return list(obj.values("slug", "name"))

    class Meta:
        model = models.EffectTag
        fields = "__all__"


class DoseUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DoseUnits
        fields = "__all__"


class AssessmentRootedSerializer(serializers.ModelSerializer):

    NO_PARENT = -1

    def get_parent(self, assessment_id, validated_data, canSelectRoot):
        parent_id = validated_data.pop("parent", self.NO_PARENT)

        parent = None
        if parent_id == self.NO_PARENT and canSelectRoot:
            parent = self.Meta.model.get_assessment_root(assessment_id)
        elif parent_id > 0:
            checkParent = self.Meta.model.objects.filter(id=parent_id).first()
            if checkParent and checkParent.get_root().name == self.Meta.model.get_assessment_root_name(
                assessment_id
            ):
                parent = checkParent

        return parent

    def create(self, validated_data):
        assessment = self.root.context["view"].assessment
        parent = self.get_parent(assessment.id, validated_data, canSelectRoot=False)
        parent_id = parent.id if parent else None

        return self.Meta.model.create_tag(assessment.id, parent_id=parent_id, **validated_data)

    def update(self, instance, validated_data):
        assessment = self.root.context["view"].assessment
        parent = self.get_parent(assessment.id, validated_data, canSelectRoot=True)

        for attr, value in list(validated_data.items()):
            setattr(instance, attr, value)
        instance.save()

        # check the following before moving:
        #   1) parent exists
        #   2) parent != self
        #   3) new parent != old parent
        #   4) new parent != descendant of self
        if (
            parent
            and instance.id != parent.id
            and parent.id != instance.get_parent().id
            and parent.id not in instance.get_descendants().values_list("id", flat=True)
        ):

            instance.move(parent, pos="last-child")

        return instance


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


class JobSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["status"] = instance.get_status_display()
        ret["job"] = instance.get_job_display()
        ret["detail_url"] = instance.get_detail_url()
        return ret

    class Meta:
        model = models.Job
        fields = "__all__"


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Log
        fields = "__all__"


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Blog
        fields = "__all__"


class StrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Strain
        fields = "__all__"
