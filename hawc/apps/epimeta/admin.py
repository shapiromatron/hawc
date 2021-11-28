from django.contrib import admin

from . import models


@admin.register(models.MetaProtocol)
class MetaProtocolAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
        "study__short_citation",
    )
    list_display = (
        "name",
        "study",
        "protocol_type",
    )


@admin.register(models.MetaResult)
class MetaResultAdmin(admin.ModelAdmin):
    list_display = (
        "protocol",
        "label",
        "data_location",
        "health_outcome",
        "exposure_name",
        "estimate",
        "lower_ci",
        "upper_ci",
    )


@admin.register(models.SingleResult)
class SingleResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "meta_result",
        "study",
        "exposure_name",
        "weight",
        "n",
        "estimate",
        "lower_ci",
        "upper_ci",
    )
    list_select_related = ("meta_result", "study")
