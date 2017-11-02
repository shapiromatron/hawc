from django.contrib import admin

from . import models


class RiskOfBiasMetricAdmin(admin.ModelAdmin):
    list_display = ('domain', 'name', 'created', 'last_updated')

class RiskOfBiasMetricAnswerAdmin(admin.ModelAdmin):
    list_display = ('metric','answer_choice', 'answer_symbol', 'answer_score', 'answer_shade', 'answer_order')

admin.site.register(models.RiskOfBiasMetric, RiskOfBiasMetricAdmin)
admin.site.register(models.RiskOfBiasMetricAnswers, RiskOfBiasMetricAnswerAdmin)
