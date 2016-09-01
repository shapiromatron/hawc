from django.apps import apps
from utils.models import BaseManager


BIOASSAY = 0
EPI = 1
EPI_META = 4
IN_VITRO = 2
OTHER = 3

STUDY_TYPE_CHOICES = (
    (BIOASSAY, 'Animal Bioassay'),
    (EPI, 'Epidemiology'),
    (EPI_META, 'Epidemiology meta-analysis/pooled analysis'),
    (IN_VITRO, 'In vitro'),
    (OTHER, 'Other'))


class VisualManager(BaseManager):
    assessment_relation = 'assessment'


class DataPivotManager(BaseManager):
    assessment_relation = 'assessment'

    def clonable_queryset(self, user):
        """
        Return data-pivots which can cloned by a specific user
        """
        Assessment = apps.get_model('assessment', 'Assessment')
        assessment_ids = Assessment.objects\
            .get_viewable_assessments(user, public=True)\
            .values_list('id', flat=True)
        return self.filter(assessment__in=assessment_ids)\
            .select_related('assessment')\
            .order_by('assessment__name', 'title')
