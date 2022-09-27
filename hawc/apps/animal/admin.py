from django.contrib import admin
from reversion.admin import VersionAdmin

from . import models


@admin.register(models.Experiment)
class ExperimentAdmin(VersionAdmin, admin.ModelAdmin):
    raw_id_fields = ("study", "dtxsid")
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
class AnimalGroupAdmin(VersionAdmin, admin.ModelAdmin):
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
    raw_id_fields = ("experiment", "species", "strain", "parents", "dosing_regime", "siblings")


class DoseGroupInline(admin.TabularInline):
    model = models.DoseGroup
    raw_id_fields = ("dose_units",)
    extra = 0


@admin.register(models.DosingRegime)
class DosingRegimeAdmin(VersionAdmin, admin.ModelAdmin):
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
    list_select_related = ("dosed_animals",)
    search_fields = ("dosed_animals__name",)
    raw_id_fields = ("dosed_animals",)
    inlines = (DoseGroupInline,)


class EndpointGroupInline(admin.TabularInline):
    model = models.EndpointGroup
    extra = 0


@admin.register(models.Endpoint)
class EndpointAdmin(VersionAdmin, admin.ModelAdmin):
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
    raw_id_fields = (
        "assessment",
        "animal_group",
        "system_term",
        "organ_term",
        "effect_term",
        "effect_subtype_term",
        "name_term",
    )
    inlines = (EndpointGroupInline,)
