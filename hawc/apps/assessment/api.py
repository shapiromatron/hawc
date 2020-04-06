import logging

import pandas as pd
from django.apps import apps
from django.core import exceptions
from django.db.models import Count
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from ..common.helper import create_uuid, tryParseInt
from ..common.renderers import PandasRenderers
from ..lit import constants
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

    @action(detail=True, methods=("patch",))
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

    @action(detail=False, methods=("get",), permission_classes=(permissions.AllowAny,))
    def public(self, request):
        queryset = self.model.objects.get_public_assessments()
        serializer = serializers.AssessmentSerializer(queryset, many=True)
        return Response(serializer.data)

    @method_decorator(cache_page(60 * 60 * 24))
    @action(detail=False, methods=("get",), renderer_classes=PandasRenderers)
    def training_data(self, request):
        Endpoint = apps.get_model("animal", "Endpoint")
        # map of django field names to friendlier column names
        column_map = {
            "assessment_id": "assessment_uuid",
            "animal_group__species__name": "species_name",
            "animal_group__strain__name": "strain_name",
            "system": None,
            "animal_group__experiment__study__title": "study_title",
            "animal_group__experiment__study__abstract": "study_abstract",
            "animal_group__experiment__study__identifiers__database": "db",
            "animal_group__experiment__study__identifiers__unique_id": "db_id",
        }
        queryset = (
            Endpoint.objects.filter(assessment__is_public_training_data=True)
            .prefetch_related(
                "animal_group",
                "animal_group__species",
                "animal_group__strain",
                "animal_group__experiment",
                "animal_group__experiment__study",
                "animal_group__experiment__study__identifiers",
            )
            .values(*column_map.keys())
        )

        df = pd.DataFrame.from_records(queryset).rename(
            columns={k: v for k, v in column_map.items() if v is not None}
        )

        # Creates a UUID for each assessment_id, providing anonymity
        df["assessment_uuid"] = df["assessment_uuid"].apply(create_uuid)

        # Assigns db_id to hero_id in all instances where db == HERO
        df["hero_id"] = None
        df["hero_id"].loc[df["db"] == constants.HERO] = df["db_id"][df["db"] == constants.HERO]

        # Assigns db_id to pubmed_id in all instances where db == PUBMED
        df["pubmed_id"] = None
        df["pubmed_id"].loc[df["db"] == constants.PUBMED] = df["db_id"][
            df["db"] == constants.PUBMED
        ]

        return Response(df.drop(columns=["db", "db_id"]).drop_duplicates())


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

    @action(detail=False)
    def growth(self, request):
        serializer = serializers.GrowthPlotSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        fig = serializer.create_figure()
        return Response(fig.to_dict())
