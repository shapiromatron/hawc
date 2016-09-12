from django.apps import apps
from utils.models import BaseManager


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
