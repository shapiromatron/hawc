from django.contrib import admin
from treebeard.admin import TreeAdmin

from . import models


@admin.register(models.ReferenceFilterTag)
class ReferenceFilterTagAdmin(TreeAdmin):
    pass
