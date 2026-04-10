from ..common.models import BaseManager

from django.db.models import QuerySet

class ExperimentQuerySet(QuerySet):
    pass

class ExperimentManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return ExperimentQuerySet(self.model, using=self._db)
