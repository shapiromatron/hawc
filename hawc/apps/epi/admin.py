from django.contrib import admin

from . import models


@admin.register(models.Criteria)
class CriteriaAdmin(admin.ModelAdmin):
    search_fields = ("description",)
    list_filter = (("assessment", admin.RelatedOnlyFieldListFilter),)
    list_display = ("id", "description", "created", "last_updated")
    raw_id_fields = ("assessment",)


@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name", "code")


@admin.register(models.AdjustmentFactor)
class AdjustmentFactorAdmin(admin.ModelAdmin):
    search_fields = ("description",)
    list_filter = (("assessment", admin.RelatedOnlyFieldListFilter),)
    list_display = ("id", "description", "created", "last_updated")
    raw_id_fields = ("assessment",)


@admin.register(models.Ethnicity)
class EthnicityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created",
        "last_updated",
    )


@admin.register(models.ResultMetric)
class ResultMetricAdmin(admin.ModelAdmin):
    list_display = (
        "metric",
        "abbreviation",
        "showForestPlot",
        "isLog",
        "reference_value",
        "order",
    )


@admin.register(models.StudyPopulation)
class StudyPopulationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "study",
        "design",
        "created",
        "last_updated",
    )
    list_filter = (
        "design",
        ("study__assessment", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("name", "study__short_citation")
    raw_id_fields = ("study",)


@admin.register(models.Outcome)
class OutcomeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "system",
        "effect",
        "created",
        "last_updated",
    )
    list_filter = (
        "system",
        ("study_population__study__assessment", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("name",)
    raw_id_fields = ("study_population",)


class GroupAdmin(admin.TabularInline):
    model = models.Group
    fk_name = "comparison_set"
    extra = 0


@admin.register(models.ComparisonSet)
class ComparisonSetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created",
        "last_updated",
    )
    list_filter = (("study_population__study__assessment", admin.RelatedOnlyFieldListFilter),)
    search_fields = ("name",)
    raw_id_fields = (
        "study_population",
        "outcome",
        "exposure",
    )
    inlines = [GroupAdmin]


class CentralTendencyAdmin(admin.TabularInline):
    model = models.CentralTendency
    fk_name = "exposure"
    extra = 0


@admin.register(models.Exposure)
class ExposureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "metric_units",
        "created",
        "last_updated",
    )
    list_filter = (
        ("metric_units", admin.RelatedOnlyFieldListFilter),
        ("study_population__study__assessment", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("name",)
    raw_id_fields = (
        "study_population",
        "dtxsid",
    )
    inlines = [CentralTendencyAdmin]


@admin.register(models.GroupNumericalDescriptions)
class GroupNumericalDescriptionsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "mean",
        "is_calculated",
        "variance",
        "lower",
        "upper",
    )
    list_filter = (
        (
            "group__comparison_set__study_population__study__assessment",
            admin.RelatedOnlyFieldListFilter,
        ),
    )
    raw_id_fields = ("group",)


class GroupResultAdmin(admin.TabularInline):
    model = models.GroupResult
    fk_name = "result"
    extra = 0
    raw_id_fields = ("group",)


@admin.register(models.Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "metric",
        "created",
        "last_updated",
    )
    list_filter = (
        ("metric", admin.RelatedOnlyFieldListFilter),
        ("outcome__study_population__study__assessment", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("name",)
    raw_id_fields = (
        "outcome",
        "comparison_set",
    )
    inlines = [GroupResultAdmin]
