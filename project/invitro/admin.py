from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from . import models


@admin.register(models.IVEndpointCategory)
class IVEndpointCategoryAdmin(TreeAdmin):
    form = movenodeform_factory(models.IVEndpointCategory)
    list_per_page = 1000


@admin.register(models.IVChemical)
class IVChemicalAdmin(admin.ModelAdmin):
    pass


@admin.register(models.IVCellType)
class IVCellTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.IVExperiment)
class IVExperimentAdmin(admin.ModelAdmin):
    pass


@admin.register(models.IVEndpoint)
class IVEndpointAdmin(admin.ModelAdmin):
    pass
