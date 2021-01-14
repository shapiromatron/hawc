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
    list_filter = ("is_overall_confidence", ("assessment", admin.RelatedOnlyFieldListFilter))
    search_fields = ("name",)


@admin.register(models.RiskOfBiasMetric)
class RiskOfBiasMetricAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "domain",
        "name",
        "required_animal",
        "required_epi",
        "required_invitro",
        "created",
    )
    list_filter = (
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
        "default_questions",
        "responses",
    )
    list_filter = ("number_of_reviewers", "default_questions", "responses")


@admin.register(models.RiskOfBias)
class RiskOfBiasAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "study",
        "final",
        "author",
        "num_scores",
        "num_override_scores",
        "active",
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

    def num_scores(self, obj):
        return obj.num_scores

    num_scores.short_description = "# scores"

    def num_override_scores(self, obj):
        return obj.num_override_scores

    num_scores.num_override_scores = "# overrides"

    list_filter = ("final", "active", "author")
    search_fields = ("study__short_citation", "author__last_name")
    raw_id_fields = ("study",)


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


@admin.register(models.RiskOfBiasScoreOverrideObject)
class RiskOfBiasScoreOverrideObjectAdmin(admin.ModelAdmin):
    list_display = ("id", "content_type", "object_id")
    list_filter = (("content_type", admin.RelatedOnlyFieldListFilter),)
    raw_id_fields = ("score",)
