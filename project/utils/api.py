from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework_extensions.mixins import ListUpdateModelMixin

from assessment.api.views import AssessmentEditViewset, InAssessmentFilter, RequiresAssessmentID, DisabledPagination
from . import views


class CleanupFieldsFilter(InAssessmentFilter):
    """
    Filters objects in Assessment on GET using InAssessmentFilter.
    Filters objects on ID on PATCH. If ID is not supplied in query_params,
    returns an empty queryset, as entire queryset is updated using Bulk Update.

    IDs must be supplied in the form ?ids=10209,10210.

    Catches AttributeError when `ids` is not supplied.
    """
    def filter_queryset(self, request, queryset, view):
        queryset = super(CleanupFieldsFilter, self).filter_queryset(request, queryset, view)
        ids = request.query_params.get('ids')\
            if (request.query_params.get('ids') is not u'')\
            else None
        try:
            ids = ids.split(',')
            filters = {'id__in': ids}
        except AttributeError:
            ids = []
            filters = {}

        if view.action not in ('list', 'retrieve'):
            filters = {'id__in': ids}

        return queryset.filter(**filters)


class CleanupFieldsBaseViewSet(views.ProjectManagerOrHigherMixin, ListUpdateModelMixin, AssessmentEditViewset):
    """
    Base Viewset for bulk updating text fields. Model should have a
    TEXT_CLEANUP_FIELDS class attribute which is list of fields.

    For bulk update, 'X-CUSTOM-BULK-OPERATION' header must be provided.

    Serializer should implement DynamicFieldsMixin.
    """
    assessment_filter_args = "assessment"
    template_name = 'assessment/endpointcleanup_list.html'
    pagination_class = DisabledPagination
    filter_backends = (CleanupFieldsFilter, )

    def get_assessment(self, request, *args, **kwargs):
        assessment_id = request.GET.get('assessment_id', None)
        if assessment_id is None:
            raise RequiresAssessmentID

        return get_object_or_404(self.parent_model, pk=assessment_id)

    @list_route(methods=['get'])
    def fields(self, request, format=None):
        """ /$model/api/cleanup/fields/?assessment_id=$id """
        cleanup_fields = self.model.TEXT_CLEANUP_FIELDS
        return Response({'text_cleanup_fields': cleanup_fields})

    def post_save_bulk(self, queryset, update_bulk_dict):
        ids = list(queryset.values_list('id', flat=True))
        queryset.model.delete_caches(ids)


class DynamicFieldsMixin(object):
    """
    A serializer mixin that takes an additional `fields` argument that controls
    which fields should be displayed.
    Usage::
        class MySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
            class Meta:
                model = MyModel
    """
    def __init__(self, *args, **kwargs):
        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)
        if self.context.get('request'):
            fields = self.context.get('request').query_params.get('fields')
            if fields:
                fields = fields.split(',')
                # Drop fields that are not specified in the `fields` argument.
                fields.extend(['id', 'name'])
                allowed = set(fields)
                existing = set(self.fields.keys())
                for field_name in existing - allowed:
                    self.fields.pop(field_name)
