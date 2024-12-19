from django.contrib import admin

from . import models


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("id", "date_executed", "created", "last_updated")
    list_filter = ("active", "version", "date_executed")
    raw_id_fields = ("endpoint",)
    show_facets = admin.ShowFacets.ALWAYS
