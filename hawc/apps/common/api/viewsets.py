from django.db import models
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ...assessment.api import DisabledPagination
from ..exceptions import ClassConfigurationException
from .filters import CleanupBulkIdFilter
from .mixins import ListUpdateModelMixin
from .permissions import CleanupFieldsPermissions, user_can_edit_object
from ..views import bulk_create_object_log


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

    def partial_update_bulk(self, request, *args, **kwargs):
        return super().partial_update_bulk(request, *args, **kwargs)

    def post_save_bulk(self, queryset, update_bulk_dict):
        ids = list(queryset.values_list("id", flat=True))
        bulk_create_object_log("Updated", queryset, self.request.user.id)
        queryset.model.delete_caches(ids)


class EditPermissionsCheckMixin:
    """
    API Viewset mixin which provides permission checking during create/update/destroy operations.

    Fires "user_can_edit_object" checks during requests to create/update/destroy. Viewsets mixing
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
