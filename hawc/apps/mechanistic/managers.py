from ..common.models import BaseManager

from django.db.models import QuerySet

class ExperimentQuerySet(QuerySet):
    pass


class ExperimentManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return ExperimentQuerySet(self.model, using=self._db)


class ChemicalQuerySet(QuerySet):
    pass


class ChemicalManager(BaseManager):
    # assessment_relation = "experiment__study__assessment"
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return ChemicalQuerySet(self.model, using=self._db)


class TestSystemQuerySet(QuerySet):
    pass


class TestSystemManager(BaseManager):
    assessment_relation = "experiment__study__assessment"

    def get_queryset(self):
        return TestSystemQuerySet(self.model, using=self._db)
