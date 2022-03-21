from django.db.models import Prefetch, QuerySet

from ..common.models import BaseManager
from . import models


class DesignQuerySet(QuerySet):
    def complete(self):
        return self.prefetch_related(
            "exposures",
            "outcomes",
            "chemicals",
            "adjustment_factors",
            Prefetch(
                "exposure_levels",
                queryset=models.ExposureLevel.objects.select_related(
                    "chemical", "exposure_measurement"
                ),
            ),
            Prefetch(
                "data_extractions",
                queryset=models.DataExtraction.objects.select_related(
                    "adjustment_factor", "outcome", "exposure_level"
                ),
            ),
        )


class DesignManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return DesignQuerySet(self.model, using=self._db)


class ChemicalManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"


class ExposureManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"


class ExposureLevelManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"


class OutcomeManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"


class AdjustmentFactorManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"


class DataExtractionManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"
