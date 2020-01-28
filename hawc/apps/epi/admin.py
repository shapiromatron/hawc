from django.contrib import admin

from . import models


@admin.register(models.Criteria)
class CriteriaAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):

    search_fields = ("name",)


@admin.register(models.AdjustmentFactor)
class AdjustmentFactorAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Ethnicity)
class EthnicityAdmin(admin.ModelAdmin):
    pass


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
