from django.contrib import admin

from . import models


class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )
    list_display_links = ('name', )


class StrainAdmin(admin.ModelAdmin):
    list_select_related = ('species', )
    list_display = ('id', 'name', 'species' )
    list_display_links = ('name', )
    list_filter = ('species', )


class DoseUnitsAdmin(admin.ModelAdmin):
    list_display = ('units',
                    'animal_dose_group_count',
                    'epi_exposure_count',
                    'invitro_experiment_count')


admin.site.register(models.Species, SpeciesAdmin)
admin.site.register(models.Strain, StrainAdmin)
admin.site.register(models.DoseUnits, DoseUnitsAdmin)
