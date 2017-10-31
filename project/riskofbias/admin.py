from django.contrib import admin

from . import models


class RiskOfBiasMetricAdmin(admin.ModelAdmin):
    list_display = ('domain', 'name', 'created', 'last_updated')

class RiskOfBiasMetricAnswerAdmin(admin.ModelAdmin):
    list_display = ('choice_one', 'choice_two', 'choice_three', 'choice_four', 'choice_five', 'choice_six')

admin.site.register(models.RiskOfBiasMetric, RiskOfBiasMetricAdmin)
admin.site.register(models.RiskOfBiasMetricAnswers, RiskOfBiasMetricAnswerAdmin)
