from django.contrib import admin

from . import models


class StudyQualityMetricAdmin(admin.ModelAdmin):
    list_display = ('domain', 'metric', 'created', 'last_updated')

admin.site.register(models.StudyQualityMetric, StudyQualityMetricAdmin)
