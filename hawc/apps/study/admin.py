from django.contrib import admin

from . import models


@admin.register(models.Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assessment_id",
        "short_citation",
        "study_identifier",
        "authors",
        "year",
        "title",
        "published",
        "editable",
        "created",
    )
    list_filter = ("published", "assessment_id")
    raw_id_fields = ("searches", "identifiers")
    search_fields = ("short_citation", "year", "title", "study_identifier")


@admin.register(models.Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "last_updated", "message", "study")
    readonly_field = ("created",)

    search_fields = ("study__name", "message")
