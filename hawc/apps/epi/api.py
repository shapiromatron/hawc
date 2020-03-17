from rest_framework import decorators, viewsets
from rest_framework.response import Response

from ..assessment.api import AssessmentLevelPermissions, AssessmentViewset
from ..assessment.models import Assessment
from ..common.api import CleanupFieldsBaseViewSet, LegacyAssessmentAdapterMixin
from ..common.renderers import PandasRenderers
from ..common.views import AssessmentPermissionsMixin
from . import exports, models, serializers


class EpiAssessmentViewset(
    AssessmentPermissionsMixin, LegacyAssessmentAdapterMixin, viewsets.GenericViewSet
):
    parent_model = Assessment
    model = models.Outcome
    permission_classes = (AssessmentLevelPermissions,)

    def get_queryset(self):
        perms = self.get_obj_perms()
        if not perms["edit"]:
            return self.model.objects.published(self.assessment)
        return self.model.objects.get_qs(self.assessment)

    @decorators.detail_route(methods=("get",), url_path="export", renderer_classes=PandasRenderers)
    def export(self, request, pk):
        """
        Retrieve epidemiology data for assessment.
        """
        self.set_legacy_attr(pk)
        exporter = exports.OutcomeComplete(self.get_queryset(), export_format="excel",)
        return Response(exporter.build_dataframe())


class StudyPopulation(AssessmentViewset):
    assessment_filter_args = "study__assessment"
    model = models.StudyPopulation
    serializer_class = serializers.StudyPopulationSerializer


class Exposure(AssessmentViewset):
    assessment_filter_args = "study_population__study__assessment"
    model = models.Exposure
    serializer_class = serializers.ExposureSerializer


class Outcome(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.Outcome
    serializer_class = serializers.OutcomeSerializer


class Result(AssessmentViewset):
    assessment_filter_args = "outcome__assessment"
    model = models.Result
    serializer_class = serializers.ResultSerializer


class ComparisonSet(AssessmentViewset):
    assessment_filter_args = "assessment"  # todo: fix
    model = models.ComparisonSet
    serializer_class = serializers.ComparisonSetSerializer


class Group(AssessmentViewset):
    assessment_filter_args = "assessment"  # todo: fix
    model = models.Group
    serializer_class = serializers.GroupSerializer


class OutcomeCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.OutcomeCleanupFieldsSerializer
    model = models.Outcome


class StudyPopulationCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.StudyPopulationCleanupFieldsSerializer
    model = models.StudyPopulation
    assessment_filter_args = "study__assessment"


class ExposureCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.ExposureCleanupFieldsSerializer
    model = models.Exposure
    assessment_filter_args = "study_population__study__assessment"
