from django.apps import apps
from treebeard.mp_tree import MP_NodeQuerySet
from utils.models import BaseManager


class SummaryTextManager(BaseManager):
    assessment_relation = 'assessment'

    """Custom manager for nodes in a Materialized Path tree."""

    def get_queryset(self):
        """Sets the custom queryset as the default."""
        return MP_NodeQuerySet(self.model).order_by('path')


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


class DataPivotUploadManager(BaseManager):
    assessment_relation = 'assessment'


class DataPivotQueryManager(BaseManager):
    assessment_relation = 'assessment'
