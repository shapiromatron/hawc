import pandas as pd
import plotly.express as px
from django import forms
from django.db.models import Count
from django.db.models.functions import Trunc
from plotly.graph_objs._figure import Figure

from ...animal.models import Endpoint
from ...assessment.models import Assessment
from ...lit.models import Reference
from ...myuser.models import HAWCUser
from ...study.models import Study
from ...summary.models import Visual
from .constants import DurationGrouper, GrowthModels


class GrowthForm(forms.Form):
    model = forms.ChoiceField(
        choices=GrowthModels.choices, initial=GrowthModels.assessment, required=False
    )
    grouper = forms.ChoiceField(
        choices=DurationGrouper.choices,
        initial=DurationGrouper.annual,
        label="Grouping frequency",
        required=False,
    )
    cumulative = forms.BooleanField(initial=False, required=False)

    def _get_df(self, Model, freq: str, field: str) -> pd.DataFrame:
        qs = (
            Model.objects.all()
            .annotate(date=Trunc(field, freq))
            .order_by("date")
            .values("date")
            .annotate(n=Count(field))
        )
        return pd.DataFrame(data=qs)

    def _get_figure(self, df: pd.DataFrame, cumulative: bool, label: str) -> Figure:
        if cumulative:
            df = df.set_index("date").cumsum().reset_index()
            title = f"Cumulative # of {label.lower()}"
        else:
            title = f"Growth of {label.lower()}"
        fn = px.bar if df.shape[0] < 300 else px.line
        return fn(df, x="date", y="n", title=title)

    def get_data(self) -> tuple[pd.DataFrame, Figure]:
        data = self.cleaned_data
        model = data["model"] or self.fields["model"].initial.value
        grouper = data["grouper"] or self.fields["grouper"].initial.value
        cumulative = data["cumulative"] or self.fields["cumulative"].initial
        if model == GrowthModels.user:
            df = self._get_df(HAWCUser, grouper, "date_joined")
            fig = self._get_figure(df, cumulative, "New users")
        elif model == GrowthModels.assessment:
            df = self._get_df(Assessment, grouper, "created")
            fig = self._get_figure(df, cumulative, "Assessments")
        elif model == GrowthModels.reference:
            df = self._get_df(Reference, grouper, "created")
            fig = self._get_figure(df, cumulative, "References")
        elif model == GrowthModels.study:
            df = self._get_df(Study, grouper, "created")
            fig = self._get_figure(df, cumulative, "Studies")
        elif model == GrowthModels.endpoint:
            df = self._get_df(Endpoint, grouper, "created")
            fig = self._get_figure(df, cumulative, "Endpoints")
        elif model == GrowthModels.visual:
            df = self._get_df(Visual, grouper, "created")
            fig = self._get_figure(df, cumulative, "Visuals")
        else:
            raise ValueError("Should not be reachable")
        return df, fig
