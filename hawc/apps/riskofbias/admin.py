from django.contrib import admin

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
    list_filter = ("is_overall_confidence", "assessment")
    search_fields = ("name",)


@admin.register(models.RiskOfBiasMetric)
class RiskOfBiasMetricAdmin(admin.ModelAdmin):
    list_display = ("id", "domain", "name", "created")
    list_filter = (
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
        "default_questions",
        "responses",
    )
    list_filter = ("number_of_reviewers", "default_questions", "responses")


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
    list_filter = ("is_default", "score")
