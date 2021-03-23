from django.db import models
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ...assessment.api import DisabledPagination
from .filters import CleanupBulkIdFilter
from .mixins import ListUpdateModelMixin
from .permissions import CleanupFieldsPermissions, user_can_edit_object


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


class PermCheckerMixin:
    """
    class to be mixed into api viewsets. Provides default "user_can_edit_object" checks during
    requests to create/update/destroy via API. Classes mixing this in should define a variable perm_checker_key
    which can be either a string or a list of strings that should be used as the source for the checks, via
    looking them up in the validated_data of the serializer.
    """

    def generate_things_to_check(self, serializer, append_self_obj):
        things_to_check = []

        # perm_checker_key can either be a string or an array of strings
        checker_keys = self.perm_checker_key
        if type(self.perm_checker_key) is str:
            checker_keys = [self.perm_checker_key]

        for checker_key in checker_keys:
            if checker_key in serializer.validated_data:
                things_to_check.append(serializer.validated_data.get(checker_key))

        if append_self_obj:
            things_to_check.append(self.get_object())

        if len(things_to_check) == 0:
            raise Exception(f"Improperly configured viewset {self}; needs defined perm_checker_key")

        return things_to_check

    def perform_create(self, serializer):
        for thing_to_check in self.generate_things_to_check(serializer, False):
            user_can_edit_object(
                thing_to_check, self.request.user, raise_exception=True,
            )
        super().perform_create(serializer)

    def perform_update(self, serializer):
        for thing_to_check in self.generate_things_to_check(serializer, True):
            user_can_edit_object(
                thing_to_check, self.request.user, raise_exception=True,
            )

        super().perform_update(serializer)

    def perform_destroy(self, instance):
        user_can_edit_object(
            instance, self.request.user, raise_exception=True,
        )
        super().perform_destroy(instance)
