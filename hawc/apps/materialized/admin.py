from django.contrib import admin
from django.db.models import Q

from ..common.admin import ReadOnlyAdmin, YesNoFilter
from . import models


class IsOverrideFilter(YesNoFilter):
    title = "is override"
    parameter_name = "is_override"
    query = Q(object_id__isnull=False)


@admin.register(models.FinalRiskOfBiasScore)
class FinalRiskOfBiasScoreAdmin(ReadOnlyAdmin):
    list_display = (
        "id",
        "score_id",
        "score_score",
        "is_override",
        "is_default",
        "metric_id",
        "riskofbias_id",
        "study_id",
        "content_type",
        "object_id",
    )
    list_filter = (
        IsOverrideFilter,
        "is_default",
        ("content_type", admin.RelatedOnlyFieldListFilter),
    )

    @admin.display(boolean=True)
    def is_override(self, obj) -> bool:
        return obj.object_id is not None
