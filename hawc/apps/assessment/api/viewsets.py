from pathlib import Path

from django.apps import apps
from django.db import transaction
from django.db.models import Count, Model
from django.http import Http404
from django.urls import reverse
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from ....services.epa.dsstox import RE_DTXSID
from ...common.api import CleanupBulkIdFilter, DisabledPagination, ListUpdateModelMixin
from ...common.exceptions import ClassConfigurationException
from ...common.helper import FlatExport, re_digits
from ...common.renderers import PandasRenderers
from ...common.views import bulk_create_object_log, create_object_log
from .. import models, serializers
from ..actions.audit import AssessmentAuditSerializer
from ..constants import AssessmentViewSetPermissions
from .filters import InAssessmentFilter
from .helper import get_assessment_from_query
from .permissions import AssessmentLevelPermissions, CleanupFieldsPermissions, user_can_edit_object

# all http methods except PUT
METHODS_NO_PUT = ["get", "post", "patch", "delete", "head", "options", "trace"]


class CleanupFieldsBaseViewSet(
    ListUpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Base ViewSet for bulk updating text fields.

    Implements three routes:

    - GET /?assessment_id=1: list data available for cleanup
    - PATCH /?assessment_id=1&ids=1,2,3: modify selected data
    - GET /fields/: list fields available for cleanup

    Model should have a TEXT_CLEANUP_FIELDS class attribute which is list of fields.
    For bulk update, 'X-CUSTOM-BULK-OPERATION' header must be provided.
    Serializer should implement DynamicFieldsMixin.
    """

    model: type[Model]
    assessment_filter_args: str
    filter_backends = (CleanupBulkIdFilter,)
    pagination_class = DisabledPagination
    permission_classes = (CleanupFieldsPermissions,)
    template_name = "assessment/endpointcleanup_list.html"

    def get_queryset(self):
        return self.model.objects.all()

    @action(detail=False, methods=["get"])
    def fields(self, request, format=None):
        """
        Return field names available for cleanup.
        """
        cleanup_fields = self.model.TEXT_CLEANUP_FIELDS
        TERM_FIELD_MAPPING = getattr(self.model, "TERM_FIELD_MAPPING", {})
        return Response(
            {"text_cleanup_fields": cleanup_fields, "term_field_mapping": TERM_FIELD_MAPPING}
        )

    def partial_update_bulk(self, request, *args, **kwargs):
        return super().partial_update_bulk(request, *args, **kwargs)

    def post_save_bulk(self, queryset, update_bulk_dict):
        ids = list(queryset.values_list("id", flat=True))
        bulk_create_object_log("Updated", queryset, self.request.user.id)
        if hasattr(queryset.model, "delete_caches"):
            queryset.model.delete_caches(ids)


class EditPermissionsCheckMixin:
    """
    API ViewSet mixin which provides permission checking during create/update/destroy operations.

    Fires "user_can_edit_object" checks during requests to create/update/destroy. ViewSets mixing
    this in can define a variable "edit_check_keys", which is a list of serializer attribute
    keys that should be used as the source for the checks.
    """

    def get_object_checks(self, serializer):
        """
        Generates a list of model objects to check permissions against. Each object returned
        can then be checked using user_can_edit_object, throwing an exception if necessary.

        Args:
            serializer: the serializer of the associated viewset

        Returns:
            List: A list of django model instances
        """
        objects = []

        # if thing already is created, check that we can edit it
        if serializer.instance and serializer.instance.pk:
            objects.append(serializer.instance)

        # additional checks on other attributes
        for checker_key in getattr(self, "edit_check_keys", []):
            if checker_key in serializer.validated_data:
                objects.append(serializer.validated_data.get(checker_key))

        # ensure we have at least one object to check
        if len(objects) == 0:
            raise ClassConfigurationException("Permission check required; nothing to check")

        return objects

    def perform_create(self, serializer):
        for object_ in self.get_object_checks(serializer):
            user_can_edit_object(object_, self.request.user, raise_exception=True)
        super().perform_create(serializer)

    def perform_update(self, serializer):
        for object_ in self.get_object_checks(serializer):
            user_can_edit_object(object_, self.request.user, raise_exception=True)
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        user_can_edit_object(instance, self.request.user, raise_exception=True)
        super().perform_destroy(instance)


class BaseAssessmentViewSet(viewsets.GenericViewSet):
    action_perms = {}
    assessment_filter_args = ""
    permission_classes = (AssessmentLevelPermissions,)
    filter_backends = (InAssessmentFilter,)
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all()


class AssessmentEditViewSet(viewsets.ModelViewSet):
    http_method_names = METHODS_NO_PUT
    assessment_filter_args = ""
    permission_classes = (AssessmentLevelPermissions,)
    action_perms = {}
    filter_backends = (InAssessmentFilter,)
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all()

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        create_object_log(
            "Created",
            serializer.instance,
            serializer.instance.get_assessment().id,
            self.request.user.id,
        )

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        create_object_log(
            "Updated",
            serializer.instance,
            serializer.instance.get_assessment().id,
            self.request.user.id,
        )

    @transaction.atomic
    def perform_destroy(self, instance):
        create_object_log("Deleted", instance, instance.get_assessment().id, self.request.user.id)
        super().perform_destroy(instance)


class AssessmentViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, BaseAssessmentViewSet):
    pass


class AssessmentRootedTagTreeViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet used with AssessmentRootedTagTree model.
    """

    http_method_names = METHODS_NO_PUT
    lookup_value_regex = re_digits
    permission_classes = (AssessmentLevelPermissions,)
    action_perms = {}

    def get_queryset(self):
        return self.model.objects.all()

    def list(self, request):
        self.filter_queryset(self.get_queryset())
        data = self.model.get_all_tags(self.assessment.id)
        return Response(data)

    @transaction.atomic
    def perform_create(self, serializer):
        # set assessment to serializer; needed to create and check permissions
        serializer.assessment = get_assessment_from_query(self.request)
        if not serializer.assessment.user_is_project_manager_or_higher(self.request.user):
            raise PermissionDenied()
        super().perform_create(serializer)
        create_object_log(
            "Created",
            serializer.instance,
            serializer.assessment.id,
            self.request.user.id,
        )

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        create_object_log(
            "Updated",
            serializer.instance,
            serializer.instance.get_assessment().id,
            self.request.user.id,
        )

    @transaction.atomic
    def perform_destroy(self, instance):
        create_object_log("Deleted", instance, instance.get_assessment().id, self.request.user.id)
        super().perform_destroy(instance)

    @transaction.atomic
    @action(
        detail=True, methods=("patch",), action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT
    )
    def move(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.moveWithinSiblingsToIndex(request.data["newIndex"])
        create_object_log(
            "Updated (moved)", instance, instance.get_assessment().id, self.request.user.id
        )
        return Response({"status": True})


class DoseUnitsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    model = models.DoseUnits
    serializer_class = serializers.DoseUnitsSerializer
    pagination_class = DisabledPagination
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all()


class Assessment(AssessmentViewSet):
    model = models.Assessment
    serializer_class = serializers.AssessmentSerializer
    assessment_filter_args = "id"

    @action(detail=False, permission_classes=(permissions.AllowAny,))
    def public(self, request):
        queryset = self.model.objects.get_public_assessments()
        serializer = serializers.AssessmentSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT)
    def endpoints(self, request, pk: int):
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
        reverse("assessment:clean_extracted_data", kwargs={"pk": instance.id})

        def add_item(count, title, url_route, modal_key):
            items.append(
                {
                    "count": count,
                    "title": title,
                    "url_cleanup_list": url_route,
                    "modal_key": modal_key,
                }
            )

        # animal
        add_item(
            instance.endpoint_count,
            "animal bioassay endpoints",
            reverse("animal:api:endpoint-cleanup-list"),
            "Endpoint",
        )

        add_item(
            apps.get_model("animal", "Experiment").objects.get_qs(instance.id).count(),
            "animal bioassay experiments",
            reverse("animal:api:experiment-cleanup-list"),
            "Experiment",
        )

        add_item(
            apps.get_model("animal", "AnimalGroup").objects.get_qs(instance.id).count(),
            "animal bioassay animal groups",
            reverse("animal:api:animal_group-cleanup-list"),
            "AnimalGroup",
        )

        add_item(
            apps.get_model("animal", "DosingRegime").objects.get_qs(instance.id).count(),
            "animal bioassay dosing regimes",
            reverse("animal:api:dosingregime-cleanup-list"),
            "AnimalGroup",
        )

        # epi
        add_item(
            instance.outcome_count,
            "epidemiological outcomes assessed",
            reverse("epi:api:outcome-cleanup-list"),
            "Outcome",
        )

        add_item(
            apps.get_model("epi", "StudyPopulation").objects.get_qs(instance.id).count(),
            "epi study populations",
            reverse("epi:api:studypopulation-cleanup-list"),
            "StudyPopulation",
        )

        add_item(
            apps.get_model("epi", "Exposure").objects.get_qs(instance.id).count(),
            "epi exposures",
            reverse("epi:api:exposure-cleanup-list"),
            "Exposure",
        )

        # epiv2
        add_item(
            apps.get_model("epiv2", "Design").objects.get_qs(instance.id).count(),
            "epi study populations",
            reverse("epiv2:api:design-cleanup-list"),
            None,
        )

        add_item(
            apps.get_model("epiv2", "Chemical").objects.get_qs(instance.id).count(),
            "epi chemicals",
            reverse("epiv2:api:chemical-cleanup-list"),
            None,
        )

        # in vitro
        add_item(
            instance.ivendpoint_count,
            "in vitro endpoints",
            reverse("invitro:api:ivendpoint-cleanup-list"),
            "IVEndpoint",
        )

        add_item(
            apps.get_model("invitro", "ivchemical").objects.get_qs(instance.id).count(),
            "in vitro chemicals",
            reverse("invitro:api:ivchemical-cleanup-list"),
            "IVChemical",
        )

        # study
        add_item(
            apps.get_model("study", "Study").objects.get_qs(instance.id).count(),
            "studies",
            reverse("study:api:study-cleanup-list"),
            "Study",
        )

        return Response({"name": instance.name, "id": instance.id, "items": items})

    @action(
        detail=True,
        url_path=r"logs/(?P<type>[\w]+)",
        action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def logs(self, request: Request, pk: int, type: str):
        instance = self.get_object()
        serializer = AssessmentAuditSerializer.from_drf(data=dict(assessment=instance, type=type))
        export = serializer.export()
        return Response(export)


class DatasetViewSet(AssessmentViewSet):
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

    @action(
        detail=True,
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def data(self, request, pk: int | None = None):
        instance = self.get_object()
        revision = instance.get_latest_revision()
        if not revision.data_exists():
            raise Http404()
        export = FlatExport(df=revision.get_df(), filename=Path(revision.metadata["filename"]).stem)
        return Response(export)

    @action(
        detail=True,
        action_perms=AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER,
        renderer_classes=PandasRenderers,
        url_path=r"version/(?P<version>\d+)",
    )
    def version(self, request, pk: int, version: int):
        instance = self.get_object()
        revision = instance.revisions.filter(version=version).first()
        if revision is None or not revision.data_exists():
            raise Http404()
        export = FlatExport(df=revision.get_df(), filename=Path(revision.metadata["filename"]).stem)
        return Response(export)


class DssToxViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    permission_classes = (permissions.AllowAny,)
    lookup_value_regex = RE_DTXSID
    model = models.DSSTox
    serializer_class = serializers.DSSToxSerializer

    def get_queryset(self):
        return self.model.objects.all()


class StrainViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    model = models.Strain
    queryset = models.Strain.objects.all()
    serializer_class = serializers.StrainSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("species",)
