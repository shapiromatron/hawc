from django.contrib import admin

from . import models


class StatisticalMetricAdmin(admin.ModelAdmin):
    list_display = ('metric', 'isLog', 'order', )

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(models.StatisticalMetric, StatisticalMetricAdmin)
