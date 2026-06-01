from django.db.models import QuerySet

from ..common.models import BaseManager


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


class MethodQuerySet(QuerySet):
    pass


class MethodManager(BaseManager):
    assessment_relation = "experiment__study__assessment"

    def get_queryset(self):
        return MethodQuerySet(self.model, using=self._db)


class TestDesignQuerySet(QuerySet):
    pass


class TestDesignManager(BaseManager):
    assessment_relation = "experiment__study__assessment"

    def get_queryset(self):
        return TestDesignQuerySet(self.model, using=self._db)


class ExperimentalDesignQuerySet(QuerySet):
    pass


class ExperimentalDesignManager(BaseManager):
    assessment_relation = "experiment__study__assessment"

    def get_queryset(self):
        return ExperimentalDesignQuerySet(self.model, using=self._db)


class DataAnalysisQuerySet(QuerySet):
    pass


class DataAnalysisManager(BaseManager):
    assessment_relation = "experiment__study__assessment"

    def get_queryset(self):
        return DataAnalysisQuerySet(self.model, using=self._db)
