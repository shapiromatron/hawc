from django.contrib import admin

from . import models


class CriteriaAdmin(admin.ModelAdmin):
    pass


class CountryAdmin(admin.ModelAdmin):

    search_fields = ("name",)


class AdjustmentFactorAdmin(admin.ModelAdmin):
    pass


class EthnicityAdmin(admin.ModelAdmin):
    pass


class ResultMetricAdmin(admin.ModelAdmin):
    list_display = (
        "metric",
        "abbreviation",
        "showForestPlot",
        "isLog",
        "reference_value",
        "order",
    )


admin.site.register(models.Criteria, CriteriaAdmin)
admin.site.register(models.Country, CountryAdmin)
admin.site.register(models.AdjustmentFactor, AdjustmentFactorAdmin)
admin.site.register(models.Ethnicity, EthnicityAdmin)
admin.site.register(models.ResultMetric, ResultMetricAdmin)
