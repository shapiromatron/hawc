from django.contrib import admin

from . import models


class RiskOfBiasMetricAdmin(admin.ModelAdmin):
    list_display = ('domain', 'name', 'created', 'last_updated')

admin.site.register(models.RiskOfBiasMetric, RiskOfBiasMetricAdmin)
