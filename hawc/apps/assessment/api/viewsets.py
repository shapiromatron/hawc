from pathlib import Path

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.db.models import Count, Model
from django.http import Http404
from django.urls import reverse
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from ....services.epa.dsstox import RE_DTXSID
from ...common.api import CleanupBulkIdFilter, DisabledPagination, ListUpdateModelMixin
from ...common.helper import FlatExport, re_digits
from ...common.renderers import PandasRenderers
from ...common.views import bulk_create_object_log, create_object_log
from .. import models, serializers
from ..actions.audit import AssessmentAuditSerializer
from ..constants import AssessmentViewSetPermissions
from ..filterset import EffectTagFilterSet, GlobalChemicalsFilterSet
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
            raise ImproperlyConfigured("Permission check required; nothing to check")

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


class Assessment(AssessmentEditViewSet):
    model = models.Assessment
    serializer_class = serializers.AssessmentSerializer
    assessment_filter_args = "id"

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        else:
            return super().get_permissions()

    @action(detail=False, permission_classes=(permissions.AllowAny,))
    def public(self, request):
        queryset = self.model.objects.all().public()
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

        def add_item(app, count, title, url_route, modal_key):
            items.append(
                {
                    "app": app,
                    "count": count,
                    "title": title,
                    "url_cleanup_list": url_route,
                    "modal_key": modal_key,
                }
            )

        # study
        add_item(
            "Study",
            apps.get_model("study", "Study").objects.get_qs(instance.id).count(),
            "Studies",
            reverse("study:api:study-cleanup-list"),
            "Study",
        )

        # animal
        add_item(
            "Bioassay",
            apps.get_model("animal", "Experiment").objects.get_qs(instance.id).count(),
            "Experiments",
            reverse("animal:api:experiment-cleanup-list"),
            "Experiment",
        )
        add_item(
            "Bioassay",
            apps.get_model("animal", "AnimalGroup").objects.get_qs(instance.id).count(),
            "Animal Groups",
            reverse("animal:api:animal_group-cleanup-list"),
            "AnimalGroup",
        )
        add_item(
            "Bioassay",
            apps.get_model("animal", "DosingRegime").objects.get_qs(instance.id).count(),
            "Dosing Regimes",
            reverse("animal:api:dosingregime-cleanup-list"),
            "AnimalGroup",
        )
        add_item(
            "Bioassay",
            instance.endpoint_count,
            "Endpoints",
            reverse("animal:api:endpoint-cleanup-list"),
            "Endpoint",
        )
        # eco
        add_item(
            "Ecology",
            apps.get_model("eco", "Design").objects.get_qs(instance.id).count(),
            "Designs",
            reverse("eco:api:design-cleanup-list"),
            "Design",
        )
        add_item(
            "Ecology",
            apps.get_model("eco", "Cause").objects.get_qs(instance.id).count(),
            "Causes",
            reverse("eco:api:cause-cleanup-list"),
            "Cause",
        )
        add_item(
            "Ecology",
            apps.get_model("eco", "Effect").objects.get_qs(instance.id).count(),
            "Effects",
            reverse("eco:api:effect-cleanup-list"),
            "Effect",
        )
        add_item(
            "Ecology",
            apps.get_model("eco", "Result").objects.get_qs(instance.id).count(),
            "Results",
            reverse("eco:api:result-cleanup-list"),
            "Results",
        )

        # epi
        add_item(
            "Epidemiology",
            apps.get_model("epi", "StudyPopulation").objects.get_qs(instance.id).count(),
            "Study Populations",
            reverse("epi:api:studypopulation-cleanup-list"),
            "StudyPopulation",
        )
        add_item(
            "Epidemiology",
            apps.get_model("epi", "Exposure").objects.get_qs(instance.id).count(),
            "Exposures",
            reverse("epi:api:exposure-cleanup-list"),
            "Exposure",
        )
        add_item(
            "Epidemiology",
            instance.outcome_count,
            "Outcomes",
            reverse("epi:api:outcome-cleanup-list"),
            "Outcome",
        )
        # epiv2
        add_item(
            "Epidemiology",
            apps.get_model("epiv2", "Design").objects.get_qs(instance.id).count(),
            "Study Populations",
            reverse("epiv2:api:design-cleanup-list"),
            None,
        )
        add_item(
            "Epidemiology",
            apps.get_model("epiv2", "Chemical").objects.get_qs(instance.id).count(),
            "Chemicals",
            reverse("epiv2:api:chemical-cleanup-list"),
            None,
        )
        add_item(
            "Epidemiology",
            apps.get_model("epiv2", "Exposure").objects.get_qs(instance.id).count(),
            "Exposures",
            reverse("epiv2:api:exposure-cleanup-list"),
            None,
        )
        add_item(
            "Epidemiology",
            apps.get_model("epiv2", "ExposureLevel").objects.get_qs(instance.id).count(),
            "Exposure Levels",
            reverse("epiv2:api:exposure-level-cleanup-list"),
            None,
        )
        add_item(
            "Epidemiology",
            apps.get_model("epiv2", "Outcome").objects.get_qs(instance.id).count(),
            "Outcomes",
            reverse("epiv2:api:outcome-cleanup-list"),
            None,
        )
        add_item(
            "Epidemiology",
            apps.get_model("epiv2", "AdjustmentFactor").objects.get_qs(instance.id).count(),
            "Adjustment Factors",
            reverse("epiv2:api:adjustment-factor-cleanup-list"),
            None,
        )
        add_item(
            "Epidemiology",
            apps.get_model("epiv2", "DataExtraction").objects.get_qs(instance.id).count(),
            "Data Extractions",
            reverse("epiv2:api:data-extraction-cleanup-list"),
            None,
        )

        # in vitro
        add_item(
            "In Vitro",
            apps.get_model("invitro", "ivchemical").objects.get_qs(instance.id).count(),
            "Chemicals",
            reverse("invitro:api:ivchemical-cleanup-list"),
            "IVChemical",
        )
        add_item(
            "In Vitro",
            instance.ivendpoint_count,
            "Endpoints",
            reverse("invitro:api:ivendpoint-cleanup-list"),
            "IVEndpoint",
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
        return serializer.export()

    @action(
        detail=False,
        permission_classes=(permissions.IsAdminUser,),
        renderer_classes=PandasRenderers,
    )
    def chemical_search(self, request):
        """Global chemical search, across all assessments."""
        queryset = models.Assessment.objects.all()
        fs = GlobalChemicalsFilterSet(request.GET, queryset=queryset)
        if not (query := fs.data.get("query")):
            raise ValidationError({"query": "No query parameters provided"})
        df = fs.qs.global_chemical_report()
        filename = f"assessment-search-{query}"
        return FlatExport.api_response(df, filename)


class EffectTagViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    model = models.EffectTag
    queryset = models.EffectTag.objects.all()
    serializer_class = serializers.EffectTagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_value_regex = re_digits
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EffectTagFilterSet


class AssessmentValueViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["assessment"]
    assessment_filter_args = "assessment"
    model = models.AssessmentValue
    serializer_class = serializers.AssessmentValueSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("assessment")


class AssessmentDetailViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["assessment"]
    assessment_filter_args = "assessment"
    model = models.AssessmentDetail
    serializer_class = serializers.AssessmentDetailSerializer


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
        return FlatExport.api_response(
            df=revision.get_df(), filename=Path(revision.metadata["filename"]).stem
        )

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
        return FlatExport.api_response(
            df=revision.get_df(), filename=Path(revision.metadata["filename"]).stem
        )


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
