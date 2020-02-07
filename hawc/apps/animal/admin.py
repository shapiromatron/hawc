from django.contrib import admin

from . import models


@admin.register(models.Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "study",
        "name",
        "type",
        "has_multiple_generations",
        "chemical",
        "cas",
        "created",
    )
    list_filter = ("type", "has_multiple_generations", "chemical", "study__assessment")
    search_fields = (
        "study__short_citation",
        "name",
    )


@admin.register(models.AnimalGroup)
class AnimalGroupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "experiment",
        "name",
        "species",
        "strain",
        "sex",
        "created",
    )
    list_filter = ("species", "strain", "sex", "experiment__study__assessment_id")
    search_fields = ("name",)


@admin.register(models.DosingRegime)
class DosingRegimeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "dosed_animals",
        "route_of_exposure",
        "duration_exposure",
        "num_dose_groups",
        "created",
    )
    list_filter = (
        "route_of_exposure",
        "num_dose_groups",
        "dosed_animals__experiment__study__assessment_id",
    )
    search_fields = ("dosed_animals__name",)


@admin.register(models.Endpoint)
class EndpointAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assessment_id",
        "animal_group",
        "name",
        "system",
        "organ",
        "effect",
        "data_extracted",
        "created",
    )
    list_filter = ("system", "organ", "data_extracted", "assessment_id")
    search_fields = ("name",)
