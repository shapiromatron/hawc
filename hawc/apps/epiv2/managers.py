from django.db.models import Prefetch, QuerySet

from ..common.models import BaseManager
from . import models


class DesignQuerySet(QuerySet):
    def complete(self):
        return self.select_related("study").prefetch_related(
            "countries",
            "exposures",
            "outcomes",
            Prefetch(
                "chemicals",
                queryset=models.Chemical.objects.select_related("dsstox"),
            ),
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
                    "factors", "outcome", "exposure_level"
                ),
            ),
        )


class DataExtractionQuerySet(QuerySet):
    def complete(self):
        return self.select_related(
            "design__study",
            "exposure_level__chemical",
            "exposure_level__exposure_measurement",
            "outcome",
            "factors",
        ).prefetch_related("design__countries")


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
    assessment_relation = "design__study__assessment"

    def get_queryset(self):
        return DataExtractionQuerySet(self.model, using=self._db)

    def published(self, assessment_id):
        return self.assessment_qs(assessment_id).filter(design__study__published=True)
