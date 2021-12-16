import logging
from pathlib import Path
from typing import Optional

import pandas as pd
from django.apps import apps
from django.core import exceptions
from django.db.models import Count
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from hawc.services.epa import dsstox

from ..common.diagnostics import worker_healthcheck
from ..common.helper import FlatExport, create_uuid, re_digits, tryParseInt
from ..common.renderers import PandasRenderers, SvgRenderer
from ..common.views import create_object_log
from ..lit import constants
from . import models, serializers
from .actions import media_metadata_report


class DisabledPagination(PageNumberPagination):
    page_size = None


logger = logging.getLogger(__name__)


class RequiresAssessmentID(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Please provide an `assessment_id` argument to your GET request."


class InvalidAssessmentID(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Assessment does not exist for given `assessment_id`."


def get_assessment_id_param(request) -> int:
    """
    If request doesn't contain an integer-based `assessment_id`, an exception is raised.
    """
    assessment_id = tryParseInt(request.GET.get("assessment_id"))
    if assessment_id is None:
        raise RequiresAssessmentID()
    return assessment_id


def get_assessment_from_query(request) -> Optional[models.Assessment]:
    """Returns assessment or raises exception if does not exist."""
    assessment_id = get_assessment_id_param(request)
    try:
        return models.Assessment.objects.get(pk=assessment_id)
    except models.Assessment.DoesNotExist:
        raise InvalidAssessmentID()


class JobPermissions(permissions.BasePermission):
    """
    Requires admin permissions where jobs have no associated assessment
    or when part of a list, and assessment level permissions when jobs
    have an associated assessment.
    """

    def has_object_permission(self, request, view, obj):
        if obj.assessment is None:
            return bool(request.user and request.user.is_staff)
        elif request.method in permissions.SAFE_METHODS:
            return obj.assessment.user_can_view_object(request.user)
        else:
            return obj.assessment.user_can_edit_object(request.user)

    def has_permission(self, request, view):
        if view.action == "list":
            return bool(request.user and request.user.is_staff)
        elif view.action == "create":
            serializer = view.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            assessment = serializer.validated_data.get("assessment")
            if assessment is None:
                return bool(request.user and request.user.is_staff)
            else:
                return assessment.user_can_edit_object(request.user)
        else:
            # other actions are object specific,
            # and will be caught by object permissions
            return True


class AssessmentLevelPermissions(permissions.BasePermission):
    default_list_actions = ["list"]

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
        list_actions = getattr(view, "list_actions", self.default_list_actions)
        if view.action in list_actions:
            logger.debug("Permission checked")

            if not hasattr(view, "assessment"):
                view.assessment = get_assessment_from_query(request)

            return view.assessment.user_can_view_object(request.user)

        return True


class AssessmentReadPermissions(AssessmentLevelPermissions):
    def has_object_permission(self, request, view, obj):
        if not hasattr(view, "assessment"):
            view.assessment = obj.get_assessment()
        return view.assessment.user_can_view_object(request.user)


class InAssessmentFilter(filters.BaseFilterBackend):
    """
    Filter objects which are in a particular assessment.
    """

    default_list_actions = ["list"]

    def filter_queryset(self, request, queryset, view):
        list_actions = getattr(view, "list_actions", self.default_list_actions)
        if view.action not in list_actions:
            return queryset

        if not hasattr(view, "assessment"):
            view.assessment = get_assessment_from_query(request)

        if not view.assessment_filter_args:
            raise ValueError("Viewset requires the `assessment_filter_args` argument")

        filters = {view.assessment_filter_args: view.assessment.id}
        return queryset.filter(**filters)


class AssessmentViewset(viewsets.ReadOnlyModelViewSet):
    assessment_filter_args = ""
    permission_classes = (AssessmentLevelPermissions,)
    filter_backends = (InAssessmentFilter,)
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all()


class AssessmentEditViewset(viewsets.ModelViewSet):
    assessment_filter_args = ""
    permission_classes = (AssessmentLevelPermissions,)
    parent_model = models.Assessment
    filter_backends = (InAssessmentFilter,)
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        create_object_log(
            "Created",
            serializer.instance,
            serializer.instance.get_assessment().id,
            self.request.user.id,
        )

    def perform_update(self, serializer):
        super().perform_update(serializer)
        create_object_log(
            "Updated",
            serializer.instance,
            serializer.instance.get_assessment().id,
            self.request.user.id,
        )

    def perform_destroy(self, instance):
        create_object_log("Deleted", instance, instance.get_assessment().id, self.request.user.id)
        super().perform_destroy(instance)


class AssessmentRootedTagTreeViewset(viewsets.ModelViewSet):
    """
    Base viewset used with utils/models/AssessmentRootedTagTree subclasses
    """

    lookup_value_regex = re_digits
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
        assessment_id = get_assessment_id_param(self.request)
        self.assessment = models.Assessment.objects.filter(id=assessment_id).first()
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
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all()


class Assessment(AssessmentViewset):
    model = models.Assessment
    serializer_class = serializers.AssessmentSerializer
    assessment_filter_args = "id"

    @action(detail=False, permission_classes=(permissions.AllowAny,))
    def public(self, request):
        queryset = self.model.objects.get_public_assessments()
        serializer = serializers.AssessmentSerializer(queryset, many=True)
        return Response(serializer.data)

    @method_decorator(cache_page(60 * 60 * 24))
    @action(detail=False, renderer_classes=PandasRenderers)
    def bioassay_ml_dataset(self, request):
        Endpoint = apps.get_model("animal", "Endpoint")
        # map of django field names to friendlier column names
        column_map = {
            "assessment_id": "assessment_uuid",
            "name": "endpoint_name",
            "animal_group__experiment__chemical": "chemical",
            "animal_group__species__name": "species",
            "animal_group__strain__name": "strain",
            "animal_group__sex": "sex",
            "system": "endpoint_system",
            "organ": "endpoint_organ",
            "effect": "endpoint_effect",
            "effect_subtype": "endpoint_effect_subtype",
            "data_location": "endpoint_data_location",
            "animal_group__experiment__study__title": "study_title",
            "animal_group__experiment__study__abstract": "study_abstract",
            "animal_group__experiment__study__full_citation": "study_full_citation",
            "animal_group__experiment__study__identifiers__database": "db",
            "animal_group__experiment__study__identifiers__unique_id": "db_id",
        }
        queryset = (
            Endpoint.objects.filter(assessment__is_public_training_data=True)
            .select_related(
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
        df.loc[df["db"] == constants.HERO, ["hero_id"]] = df["db_id"][df["db"] == constants.HERO]

        # Assigns db_id to pubmed_id in all instances where db == PUBMED
        df["pubmed_id"] = None
        df.loc[df["db"] == constants.PUBMED, ["pubmed_id"]] = df["db_id"][
            df["db"] == constants.PUBMED
        ]
        df = df.drop(columns=["db", "db_id"]).drop_duplicates()
        today = timezone.now().strftime("%Y-%m-%d")
        export = FlatExport(df=df, filename=f"hawc-bioassay-dataset-{today}")
        return Response(export)

    @action(detail=True)
    def endpoints(self, request, pk: int = None):
        """
        Optimized for queryset speed; some counts in get_queryset
        and others in the list here; depends on if a "select distinct" is
        required which significantly decreases query speed.
        """

        # check permissions
        instance = self.get_object()

        # re-query w/ annotations
        instance = (
            self.model.objects.get_qs(instance.id)
            .annotate(endpoint_count=Count("baseendpoint__endpoint"))
            .annotate(outcome_count=Count("baseendpoint__outcome"))
            .annotate(ivendpoint_count=Count("baseendpoint__ivendpoint"))
        ).first()

        items = []
        app_url = reverse("assessment:clean_extracted_data", kwargs={"pk": instance.id})

        # animal
        items.append(
            {
                "count": instance.endpoint_count,
                "title": "animal bioassay endpoints",
                "type": "ani",
                "url": f"{app_url}ani/",
                "url_cleanup_list": reverse("animal:api:endpoint-cleanup-list"),
                "modal_key": "Endpoint",
            }
        )

        count = apps.get_model("animal", "Experiment").objects.get_qs(instance.id).count()
        items.append(
            {
                "count": count,
                "title": "animal bioassay experiments",
                "type": "experiment",
                "url": f"{app_url}experiment/",
                "url_cleanup_list": reverse("animal:api:experiment-cleanup-list"),
                "modal_key": "Experiment",
            }
        )

        count = apps.get_model("animal", "AnimalGroup").objects.get_qs(instance.id).count()
        items.append(
            {
                "count": count,
                "title": "animal bioassay animal groups",
                "type": "animal-groups",
                "url": f"{app_url}animal-groups/",
                "url_cleanup_list": reverse("animal:api:animal_group-cleanup-list"),
                "modal_key": "AnimalGroup",
            }
        )

        count = apps.get_model("animal", "DosingRegime").objects.get_qs(instance.id).count()
        items.append(
            {
                "count": count,
                "title": "animal bioassay dosing regimes",
                "type": "dosing-regime",
                "url": f"{app_url}dosing-regime/",
                "url_cleanup_list": reverse("animal:api:dosingregime-cleanup-list"),
                "modal_key": "AnimalGroup",
            }
        )

        # epi
        items.append(
            {
                "count": instance.outcome_count,
                "title": "epidemiological outcomes assessed",
                "type": "epi",
                "url": f"{app_url}epi/",
                "url_cleanup_list": reverse("epi:api:outcome-cleanup-list"),
                "modal_key": "Outcome",
            }
        )

        count = apps.get_model("epi", "StudyPopulation").objects.get_qs(instance.id).count()
        items.append(
            {
                "count": count,
                "title": "epi study populations",
                "type": "study-populations",
                "url": f"{app_url}study-populations/",
                "url_cleanup_list": reverse("epi:api:studypopulation-cleanup-list"),
                "modal_key": "StudyPopulation",
            }
        )

        count = apps.get_model("epi", "Exposure").objects.get_qs(instance.id).count()
        items.append(
            {
                "count": count,
                "title": "epi exposures",
                "type": "exposures",
                "url": f"{app_url}exposures/",
                "url_cleanup_list": reverse("epi:api:exposure-cleanup-list"),
                "modal_key": "Exposure",
            }
        )

        # in vitro
        items.append(
            {
                "count": instance.ivendpoint_count,
                "title": "in vitro endpoints",
                "type": "in-vitro",
                "url": f"{app_url}in-vitro/",
                "url_cleanup_list": reverse("invitro:api:ivendpoint-cleanup-list"),
                "modal_key": "IVEndpoint",
            }
        )

        count = apps.get_model("invitro", "ivchemical").objects.get_qs(instance.id).count()
        items.append(
            {
                "count": count,
                "title": "in vitro chemicals",
                "type": "in-vitro-chemical",
                "url": f"{app_url}in-vitro-chemical/",
                "url_cleanup_list": reverse("invitro:api:ivchemical-cleanup-list"),
                "modal_key": "IVChemical",
            }
        )

        # study
        count = apps.get_model("study", "Study").objects.get_qs(instance.id).count()
        items.append(
            {
                "count": count,
                "title": "studies",
                "type": "study",
                "url": f"{app_url}study/",
                "url_cleanup_list": reverse("study:api:study-cleanup-list"),
                "modal_key": "Study",
            }
        )

        # lit
        count = apps.get_model("lit", "Reference").objects.get_qs(instance.id).count()
        items.append(
            {
                "count": count,
                "title": "references",
                "type": "reference",
                "url": f"{app_url}reference/",
                "url_cleanup_list": reverse("lit:api:reference-cleanup-list"),
                "modal_key": "Study",
            }
        )

        return Response({"name": instance.name, "id": instance.id, "items": items})

    @action(
        detail=True, methods=("get", "post"),
    )
    def jobs(self, request, pk: int = None):
        instance = self.get_object()
        if request.method == "GET":
            queryset = instance.jobs.all()
            serializer = serializers.JobSerializer(queryset, many=True)
            return Response(serializer.data)
        elif request.method == "POST":
            request.data["assessment"] = instance.id
            serializer = serializers.JobSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True)
    def logs(self, request, pk: int = None):
        instance = self.get_object()
        queryset = instance.logs.all()
        serializer = serializers.LogSerializer(queryset, many=True)
        return Response(serializer.data)


class DatasetViewset(AssessmentViewset):
    model = models.Dataset
    serializer_class = serializers.DatasetSerializer
    assessment_filter_args = "assessment_id"

    def check_object_permissions(self, request, obj):
        if not obj.user_can_view(request.user):
            raise PermissionDenied()
        return super().check_object_permissions(request, obj)

    def get_queryset(self):
        if self.action == "list":
            if not self.assessment.user_can_edit_object(self.request.user):
                return self.model.objects.get_qs(self.assessment).filter(published=True)
            return self.model.objects.get_qs(self.assessment)
        return self.model.objects.all()

    @action(detail=True, renderer_classes=PandasRenderers)
    def data(self, request, pk: int = None):
        instance = self.get_object()
        revision = instance.get_latest_revision()
        if not revision.data_exists():
            raise Http404()
        export = FlatExport(df=revision.get_df(), filename=Path(revision.metadata["filename"]).stem)
        return Response(export)

    @action(detail=True, renderer_classes=PandasRenderers, url_path=r"version/(?P<version>\d+)")
    def version(self, request, pk: int, version: int):
        instance = self.get_object()
        if not self.assessment.user_is_team_member_or_higher(request.user):
            raise PermissionDenied()
        revision = instance.revisions.filter(version=version).first()
        if revision is None or not revision.data_exists():
            raise Http404()
        export = FlatExport(df=revision.get_df(), filename=Path(revision.metadata["filename"]).stem)
        return Response(export)


class AdminDashboardViewset(viewsets.ViewSet):

    permission_classes = (permissions.IsAdminUser,)
    renderer_classes = (JSONRenderer,)

    @action(detail=False)
    def growth(self, request):
        serializer = serializers.GrowthPlotSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        fig = serializer.create_figure()
        return Response(fig.to_dict())

    @method_decorator(cache_page(60 * 60))
    @action(detail=False, url_path="assessment-size", renderer_classes=PandasRenderers)
    def assessment_size(self, request):
        df = models.Assessment.size_df()
        export = FlatExport(df=df, filename="assessment-size")
        return Response(export)

    @action(detail=False, renderer_classes=PandasRenderers)
    def media(self, request):
        uri = request.build_absolute_uri(location="/")[:-1]
        df = media_metadata_report(uri)
        export = FlatExport(df=df, filename=f"media-{timezone.now().strftime('%Y-%m-%d')}")
        return Response(export)


class DssToxViewset(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    permission_classes = (permissions.AllowAny,)
    lookup_value_regex = dsstox.RE_DTXSID
    model = models.DSSTox
    serializer_class = serializers.DSSToxSerializer

    def get_queryset(self):
        return self.model.objects.all()


class JobViewset(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    model = models.Job
    serializer_class = serializers.JobSerializer
    permission_classes = (JobPermissions,)
    pagination_class = None

    def get_queryset(self):
        if self.action == "list":
            return self.model.objects.filter(assessment=None)
        else:
            return self.model.objects.all()


class LogViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    model = models.Log
    permission_classes = (IsAdminUser,)
    serializer_class = serializers.LogSerializer
    pagination_class = None

    def get_queryset(self):
        return self.model.objects.filter(assessment=None)


class StrainViewset(viewsets.ViewSet):
    model = models.Strain

    @action(detail=False)
    def get_strains(self, request):
        strains = []
        try:
            sp = models.Species.objects.get(pk=request.GET.get("species"))
            strains = list(self.model.objects.filter(species=sp).values("id", "name"))
        except Exception:
            pass
        return Response(strains)


class HealthcheckViewset(viewsets.ViewSet):
    @action(detail=False)
    def web(self, request):
        return Response({"healthy": True})

    @action(detail=False)
    def worker(self, request):
        is_healthy = worker_healthcheck.healthy()
        # don't use 5xx email; django logging catches and sends error emails
        status_code = status.HTTP_200_OK if is_healthy else status.HTTP_400_BAD_REQUEST
        return Response({"healthy": is_healthy}, status=status_code)

    @action(
        detail=False,
        url_path="worker-plot",
        renderer_classes=(SvgRenderer,),
        permission_classes=(permissions.IsAdminUser,),
    )
    def worker_plot(self, request):
        ax = worker_healthcheck.plot()
        return Response(ax)

    @action(detail=False, url_path="worker-stats", permission_classes=(permissions.IsAdminUser,))
    def worker_stats(self, request):
        return Response(worker_healthcheck.stats())
