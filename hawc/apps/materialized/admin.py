from django.contrib import admin

from ..common.admin import ReadOnlyAdmin
from . import models


class IsOverrideFilter(admin.SimpleListFilter):
    title = "is override"
    parameter_name = "is_override"

    def lookups(self, request, model_admin):
        return (
            ("Yes", "Yes"),
            ("No", "No"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.filter(object_id__isnull=False)
        elif value == "No":
            return queryset.filter(object_id__isnull=True)
        return queryset


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

    def is_override(self, obj):
        return obj.object_id is not None

    is_override.boolean = True
