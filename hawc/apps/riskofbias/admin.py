from django.contrib import admin

from ..common.admin import YesNoFilter
from . import models


@admin.register(models.RiskOfBiasDomain)
class RiskOfBiasDomainAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assessment",
        "name",
        "is_overall_confidence",
        "created",
    )
    list_filter = ("is_overall_confidence", ("assessment", admin.RelatedOnlyFieldListFilter))
    search_fields = ("name",)


@admin.register(models.RiskOfBiasMetric)
class RiskOfBiasMetricAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "domain",
        "name",
        "responses",
        "required_animal",
        "required_epi",
        "required_invitro",
        "created",
    )
    list_filter = (
        "responses",
        "required_animal",
        "required_epi",
        "required_invitro",
        "domain__name",
        "domain__assessment_id",
    )
    search_fields = ("name",)


@admin.register(models.RiskOfBiasAssessment)
class RiskOfBiasAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assessment",
        "number_of_reviewers",
    )
    list_filter = ("number_of_reviewers",)


class RiskOfBiasScoreInlineAdmin(admin.TabularInline):
    model = models.RiskOfBiasScore
    raw_id_fields = ("metric",)
    extra = 0
    can_delete = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("metric")


@admin.register(models.RiskOfBias)
class RiskOfBiasAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "study",
        "author",
        "num_scores",
        "num_override_scores",
        "active",
        "final",
        "created",
        "last_updated",
    )
    list_select_related = (
        "study",
        "author",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.num_scores().num_override_scores()

    @admin.display(description="# scores")
    def num_scores(self, obj):
        return obj.num_scores

    def num_override_scores(self, obj):
        return obj.num_override_scores

    num_scores.num_override_scores = "# overrides"

    list_filter = ("final", "active", "author")
    search_fields = ("study__short_citation", "author__last_name")
    raw_id_fields = ("study",)
    inlines = [RiskOfBiasScoreInlineAdmin]


class RiskOfBiasScoreOverrideObjectInline(admin.TabularInline):
    model = models.RiskOfBiasScoreOverrideObject
    fk_name = "score"
    extra = 0


@admin.register(models.RiskOfBiasScore)
class RiskOfBiasScoreAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "riskofbias_id",
        "metric_id",
        "is_default",
        "label",
        "score",
    )
    list_filter = (
        "is_default",
        "score",
    )
    raw_id_fields = (
        "riskofbias",
        "metric",
    )
    inlines = [RiskOfBiasScoreOverrideObjectInline]


class IsOrphanedFilter(YesNoFilter):
    title = "Orphaned"
    parameter_name = "orphaned"
    query = -1

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.orphaned()
        elif value == "No":
            return queryset.not_orphaned()
        return queryset


@admin.register(models.RiskOfBiasScoreOverrideObject)
class RiskOfBiasScoreOverrideObjectAdmin(admin.ModelAdmin):
    list_display = ("id", "content_type", "object_id")
    list_filter = (("content_type", admin.RelatedOnlyFieldListFilter), IsOrphanedFilter)
    raw_id_fields = ("score",)
    search_fields = ("object_id",)
