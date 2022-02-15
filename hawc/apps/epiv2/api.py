from ..assessment.api import AssessmentEditViewset
from ..common.api.viewsets import EditPermissionsCheckMixin
from . import models, serializers


class Design(EditPermissionsCheckMixin, AssessmentEditViewset):
    edit_check_keys = ["study"]
    assessment_filter_args = "study__assessment"
    model = models.Design
    serializer_class = serializers.DesignSerializer

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.all()
