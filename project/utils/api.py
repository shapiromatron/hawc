from __future__ import absolute_import

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from assessment.api.views import AssessmentViewset


class DisabledPagination(PageNumberPagination):
    page_size = None

class CleanupFieldsApiView(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = None
    serializer_class = None

    # Only return model class field, instead of same field for each instance
    def list(self, request, format=None):
        cleanup_fields = self.model.text_cleanup_fields()
        return Response({'text_cleanup_fields': cleanup_fields})
