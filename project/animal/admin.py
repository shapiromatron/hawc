from django.contrib import admin

from . import models


class SpeciesAdmin(admin.ModelAdmin):
    pass


class StrainAdmin(admin.ModelAdmin):
    pass


class DoseUnitsAdmin(admin.ModelAdmin):
    list_display = ('units',
                    'animal_dose_group_count',
                    'epi_exposure_count',
                    'invitro_experiment_count')


admin.site.register(models.Species, SpeciesAdmin)
admin.site.register(models.Strain, StrainAdmin)
admin.site.register(models.DoseUnits, DoseUnitsAdmin)
