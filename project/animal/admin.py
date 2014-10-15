from django.contrib import admin

from . import models


class SpeciesAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Species, SpeciesAdmin)


class StrainAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Strain, StrainAdmin)


class DoseUnitsAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.DoseUnits, DoseUnitsAdmin)
