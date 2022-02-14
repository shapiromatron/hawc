import logging
from pathlib import Path
from typing import Optional

from django.apps import apps
from django.core import exceptions
from django.db.models import Count
from django.http import Http404
from django.urls import reverse
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from hawc.services.epa import dsstox

from ..common.diagnostics import worker_healthcheck
from ..common.helper import FlatExport, re_digits, tryParseInt
from ..common.renderers import PandasRenderers, SvgRenderer
from ..common.views import create_object_log
from . import models, serializers


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


# all http methods except PUT
METHODS_NO_PUT = ["get", "post", "patch", "delete", "head", "options", "trace"]


class AssessmentEditViewset(viewsets.ModelViewSet):
    http_method_names = METHODS_NO_PUT
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

    http_method_names = METHODS_NO_PUT

    lookup_value_regex = re_digits
    permission_classes = (AssessmentLevelPermissions,)

    PROJECT_MANAGER = "PROJECT_MANAGER"
    TEAM_MEMBER = "TEAM_MEMBER"
    create_requires = TEAM_MEMBER

    def get_queryset(self):
        return self.model.objects.all()

    def list(self, request):
        self.filter_queryset(self.get_queryset())
        data = self.model.get_all_tags(self.assessment.id)
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


class DoseUnitsViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
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


class DssToxViewset(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    permission_classes = (permissions.AllowAny,)
    lookup_value_regex = dsstox.RE_DTXSID
    model = models.DSSTox
    serializer_class = serializers.DSSToxSerializer

    def get_queryset(self):
        return self.model.objects.all()


class StrainViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    model = models.Strain
    queryset = models.Strain.objects.all()
    serializer_class = serializers.StrainSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("species",)


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
