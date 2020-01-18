from django.contrib import admin

from treebeard.admin import TreeAdmin

from . import models


class ReferenceFilterTagAdmin(TreeAdmin):
    pass


admin.site.register(models.ReferenceFilterTag, ReferenceFilterTagAdmin)
