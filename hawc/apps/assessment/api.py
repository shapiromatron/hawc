import logging
from pathlib import Path
from typing import Optional

from django.core import exceptions
from django.http import Http404
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

from ..common.helper import FlatExport, re_digits, tryParseInt
from ..common.renderers import PandasRenderers
from . import actions, models, serializers


class DisabledPagination(PageNumberPagination):
    page_size = None


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
            logging.info("Permission checked")

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


class AssessmentRootedTagTreeViewset(viewsets.ModelViewSet):
    """
    Base viewset used with utils/models/AssessmentRootedTagTree subclasses
    """

    lookup_value_regex = re_digits
    permission_classes = (AssessmentLevelPermissions,)

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
        if not self.assessment.user_can_edit_object(request.user):
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
        df = actions.bioassay_ml_dataset()
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
        assessment = self.get_object()
        payload = actions.endpoint_cleanup_metadata(assessment)
        return Response(payload)

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

    @action(
        detail=True, methods=("get",),
    )
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
        df = actions.media_metadata_report(uri)
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


class HealthcheckViewset(viewsets.ViewSet):
    def list(self, request):
        return Response({"status": "ok"})
