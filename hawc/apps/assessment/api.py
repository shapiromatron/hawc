import logging

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.apps import apps
from django.core import exceptions
from django.core.urlresolvers import reverse
from django.db.models import Count
from plotly.subplots import make_subplots
from rest_framework import decorators, filters, permissions, status, viewsets
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from ..common.helper import tryParseInt
from . import models, serializers


class RequiresAssessmentID(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Please provide an `assessment_id` argument to your GET request."


class DisabledPagination(PageNumberPagination):
    page_size = None


def get_assessment_from_query(request):
    """Returns assessment or None."""
    assessment_id = tryParseInt(request.GET.get("assessment_id"))
    if assessment_id is None:
        raise RequiresAssessmentID

    return models.Assessment.objects.get_qs(assessment_id).first()


class AssessmentLevelPermissions(permissions.BasePermission):

    list_actions = [
        "list",
    ]

    def has_object_permission(self, request, view, obj):
        if not hasattr(view, "assessment"):
            view.assessment = obj.get_assessment()
        if request.method in permissions.SAFE_METHODS:
            return view.assessment.user_can_view_object(request.user)
        elif obj == view.assessment:
            return view.assessment.user_can_edit_assessment(request.user)
        else:
            return view.assessment.user_can_edit_object(request.user)

    def has_permission(self, request, view):
        if view.action in self.list_actions:
            logging.info("Permission checked")

            if not hasattr(view, "assessment"):
                view.assessment = get_assessment_from_query(request)

            if view.assessment is None:
                return False

            return view.assessment.user_can_view_object(request.user)

        return True


class InAssessmentFilter(filters.BaseFilterBackend):
    """
    Filter objects which are in a particular assessment.
    """

    def filter_queryset(self, request, queryset, view):
        list_actions = getattr(view, "list_actions", ["list"])
        if view.action not in list_actions:
            return queryset

        if not hasattr(view, "assessment"):
            view.assessment = get_assessment_from_query(request)

        filters = {view.assessment_filter_args: view.assessment.id}
        return queryset.filter(**filters)


class AssessmentViewset(viewsets.ReadOnlyModelViewSet):
    assessment_filter_args = ""
    permission_classes = (AssessmentLevelPermissions,)
    filter_backends = (InAssessmentFilter,)

    def get_queryset(self):
        return self.model.objects.all()


class AssessmentEditViewset(viewsets.ModelViewSet):
    assessment_filter_args = ""
    permission_classes = (AssessmentLevelPermissions,)
    parent_model = models.Assessment
    filter_backends = (InAssessmentFilter,)

    def get_queryset(self):
        return self.model.objects.all()


class AssessmentRootedTagTreeViewset(viewsets.ModelViewSet):
    """
    Base viewset used with utils/models/AssessmentRootedTagTree subclasses
    """

    permission_classes = (AssessmentLevelPermissions,)

    PROJECT_MANAGER = "PROJECT_MANAGER"
    TEAM_MEMBER = "TEAM_MEMBER"
    create_requires = TEAM_MEMBER

    def get_queryset(self):
        return self.model.objects.all()

    def list(self, request):
        self.filter_queryset(self.get_queryset())
        data = self.model.get_all_tags(self.assessment.id, json_encode=False)
        return Response(data)

    def create(self, request, *args, **kwargs):
        # get an assessment
        assessment_id = tryParseInt(request.data.get("assessment_id"), -1)
        self.assessment = models.Assessment.objects.get_qs(assessment_id).first()
        if self.assessment is None:
            raise RequiresAssessmentID

        self.check_editing_permission(request)

        return super().create(request, *args, **kwargs)

    @decorators.detail_route(methods=("patch",))
    def move(self, request, *args, **kwargs):
        instance = self.get_object()
        self.assessment = instance.get_assessment()
        self.check_editing_permission(request)
        instance.moveWithinSiblingsToIndex(request.data["newIndex"])
        return Response({"status": True})

    def check_editing_permission(self, request):
        if self.create_requires == self.PROJECT_MANAGER:
            permissions_check = self.assessment.user_can_edit_assessment
        elif self.create_requires == self.TEAM_MEMBER:
            permissions_check = self.assessment.user_can_edit_object
        else:
            raise ValueError("invalid configuration of `create_requires`")

        if not permissions_check(request.user):
            raise exceptions.PermissionDenied()


class DoseUnitsViewset(viewsets.ReadOnlyModelViewSet):
    model = models.DoseUnits
    serializer_class = serializers.DoseUnitsSerializer
    pagination_class = DisabledPagination

    def get_queryset(self):
        return self.model.objects.all()


class Assessment(AssessmentViewset):
    model = models.Assessment
    permission_classes = (AssessmentLevelPermissions,)
    serializer_class = serializers.AssessmentSerializer


class AssessmentEndpointList(AssessmentViewset):
    serializer_class = serializers.AssessmentEndpointSerializer
    assessment_filter_args = "id"
    model = models.Assessment
    pagination_class = DisabledPagination

    def list(self, request, *args, **kwargs):
        """
        List has been optimized for queryset speed; some counts in get_queryset
        and others in the list here; depends on if a "select distinct" is
        required which significantly decreases query speed.
        """

        instance = self.filter_queryset(self.get_queryset())[0]
        app_url = reverse("assessment:clean_extracted_data", kwargs={"pk": instance.id})
        instance.items = []

        # animal
        instance.items.append(
            {
                "count": instance.endpoint_count,
                "title": "animal bioassay endpoints",
                "type": "ani",
                "url": f"{app_url}ani/",
            }
        )

        count = apps.get_model("animal", "Experiment").objects.get_qs(instance.id).count()
        instance.items.append(
            {
                "count": count,
                "title": "animal bioassay experiments",
                "type": "experiment",
                "url": f"{app_url}experiment/",
            }
        )

        count = apps.get_model("animal", "AnimalGroup").objects.get_qs(instance.id).count()
        instance.items.append(
            {
                "count": count,
                "title": "animal bioassay animal groups",
                "type": "animal-groups",
                "url": f"{app_url}animal-groups/",
            }
        )

        count = apps.get_model("animal", "DosingRegime").objects.get_qs(instance.id).count()
        instance.items.append(
            {
                "count": count,
                "title": "animal bioassay dosing regimes",
                "type": "dosing-regime",
                "url": f"{app_url}dosing-regime/",
            }
        )

        # epi
        instance.items.append(
            {
                "count": instance.outcome_count,
                "title": "epidemiological outcomes assessed",
                "type": "epi",
                "url": f"{app_url}epi/",
            }
        )

        count = apps.get_model("epi", "StudyPopulation").objects.get_qs(instance.id).count()
        instance.items.append(
            {
                "count": count,
                "title": "epi study populations",
                "type": "study-populations",
                "url": f"{app_url}study-populations/",
            }
        )

        count = apps.get_model("epi", "Exposure").objects.get_qs(instance.id).count()
        instance.items.append(
            {
                "count": count,
                "title": "epi exposures",
                "type": "exposures",
                "url": f"{app_url}exposures/",
            }
        )

        # in vitro
        instance.items.append(
            {
                "count": instance.ivendpoint_count,
                "title": "in vitro endpoints",
                "type": "in-vitro",
                "url": f"{app_url}in-vitro/",
            }
        )

        count = apps.get_model("invitro", "ivchemical").objects.get_qs(instance.id).count()
        instance.items.append(
            {
                "count": count,
                "title": "in vitro chemicals",
                "type": "in-vitro-chemical",
                "url": f"{app_url}in-vitro-chemical/",
            }
        )

        # study
        count = apps.get_model("study", "Study").objects.get_qs(instance.id).count()
        instance.items.append(
            {"count": count, "title": "studies", "type": "study", "url": f"{app_url}study/"}
        )

        # lit
        count = apps.get_model("lit", "Reference").objects.get_qs(instance.id).count()
        instance.items.append(
            {
                "count": count,
                "title": "references",
                "type": "reference",
                "url": f"{app_url}reference/",
            }
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        id_ = tryParseInt(self.request.GET.get("assessment_id"))
        queryset = (
            self.model.objects.get_qs(id_)
            .annotate(endpoint_count=Count("baseendpoint__endpoint"))
            .annotate(outcome_count=Count("baseendpoint__outcome"))
            .annotate(ivendpoint_count=Count("baseendpoint__ivendpoint"))
        )
        return queryset


class AdminDashboardViewset(viewsets.ViewSet):

    permission_classes = (permissions.IsAdminUser,)
    renderer_classes = (JSONRenderer,)

    def _quarterly_change_plots(self, df: pd.DataFrame, y_axis: str) -> go.Figure:

        df1 = df.set_index("date").groupby(pd.Grouper(freq="Q")).count().cumsum().reset_index()
        df2 = (
            df.set_index("date")
            .groupby(pd.Grouper(freq="Q"))
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
                f"Quarterly growth of {y_axis.lower()}",
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

    @decorators.list_route()
    def user_growth(self, request):
        fields = ("id", "date_joined")
        data = list(apps.get_model("myuser", "HAWCUser").objects.values_list(*fields))
        df = pd.DataFrame(data, columns=fields).rename(columns=dict(date_joined="date"))
        fig = self._quarterly_change_plots(df, "New users")
        return Response(fig.to_dict())

    @decorators.list_route()
    def assessment_growth(self, request):
        fields = ("id", "created")
        data = list(apps.get_model("assessment", "Assessment").objects.values_list(*fields))
        df = pd.DataFrame(data, columns=fields).rename(columns=dict(created="date"))
        fig = self._quarterly_change_plots(df, "Assessments")
        return Response(fig.to_dict())

    @decorators.list_route()
    def study_growth(self, request):
        fields = ("id", "created")
        data = list(apps.get_model("study", "Study").objects.values_list(*fields))
        df = pd.DataFrame(data, columns=fields).rename(columns=dict(created="date"))
        fig = self._quarterly_change_plots(df, "Studies")
        return Response(fig.to_dict())
