from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, filters, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework_extensions.mixins import ListUpdateModelMixin

from ..assessment.api import DisabledPagination, get_assessment_from_query
from .helper import try_parse_list_ints


class OncePerMinuteThrottle(UserRateThrottle):
    rate = "1/min"


class CleanupBulkIdFilter(filters.BaseFilterBackend):
    """
    Filters objects in Assessment on GET using InAssessmentFilter.
    Filters objects on ID on PATCH. If ID is not supplied in query_params,
    returns an empty queryset, as entire queryset is updated using Bulk Update.

    IDs must be supplied in the form ?ids=10209,10210.

    """

    def filter_queryset(self, request, queryset, view):
        if not view.assessment_filter_args:
            raise ValueError("Viewset requires the `assessment_filter_args` argument")

        # always filter queryset by `assessment_id`
        queryset = queryset.filter(**{view.assessment_filter_args: view.assessment.id})

        # required header for bulk-update
        if request._request.method.lower() == "patch":
            ids = list(set(try_parse_list_ints(request.query_params.get("ids"))))
            queryset = queryset.filter(id__in=ids)

            # invalid IDs
            if queryset.count() != len(ids):
                raise exceptions.PermissionDenied()

        return queryset


class CleanupFieldsPermissions(permissions.BasePermission):
    """
    Custom permissions for bulk-cleanup view. No object-level permissions. Here we check that
    the user has permission to edit content for this assessment, but not necessarily that they
    can edit the specific ids selected.
    """

    def has_object_permission(self, request, view, obj):
        # no object-specific permissions
        return False

    def has_permission(self, request, view):
        # must be team-member or higher to bulk-edit
        view.assessment = get_assessment_from_query(request)
        return view.assessment.user_can_edit_object(request.user)


class CleanupFieldsBaseViewSet(
    ListUpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet,
):
    """
    Base Viewset for bulk updating text fields.

    Implements three routes:

    - GET /?assessment_id=1: list data available for cleanup
    - PATCH /?assessment_id=1&ids=1,2,3: modify selected data
    - GET /fields/: list fields available for cleanup

    Model should have a TEXT_CLEANUP_FIELDS class attribute which is list of fields.
    For bulk update, 'X-CUSTOM-BULK-OPERATION' header must be provided.
    Serializer should implement DynamicFieldsMixin.
    """

    model: models.Model = None  # must be added
    assessment_filter_args: str = ""  # must be added
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

    def post_save_bulk(self, queryset, update_bulk_dict):
        ids = list(queryset.values_list("id", flat=True))
        queryset.model.delete_caches(ids)


class DynamicFieldsMixin:
    """
    A serializer mixin that takes an additional `fields` argument that controls
    which fields should be displayed.
    Usage::
        class MySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
            class Meta:
                model = MyModel
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get("request"):
            fields = self.context.get("request").query_params.get("fields")
            if fields:
                fields = fields.split(",")
                # Drop fields that are not specified in the `fields` argument.
                fields.extend(["id", "name"])
                allowed = set(fields)
                existing = set(self.fields.keys())
                for field_name in existing - allowed:
                    self.fields.pop(field_name)


class LegacyAssessmentAdapterMixin:
    """
    A mixin that allows API viewsets to interact with legacy methods.
    """

    def set_legacy_attr(self, pk):
        self.parent = get_object_or_404(self.parent_model, pk=pk)
        self.assessment = self.parent.get_assessment()


def user_can_edit_object(
    instance: models.Model, user: models.Model, raise_exception: bool = False
) -> bool:
    """Permissions check to ensure that user can edit assessment objects

    Args:
        instance (models.Model): The instance to check
        user (models.Model): The user instance
        raise_exception (bool, optional): Throw an Exception; defaults to False.

    Raises:
        exceptions.PermissionDenied: If raise_exc is True and user doesn't have permission

    """
    can_edit = instance.get_assessment().user_can_edit_object(user)
    if raise_exception and not can_edit:
        raise exceptions.PermissionDenied("Invalid permission to edit assessment.")
    return can_edit
