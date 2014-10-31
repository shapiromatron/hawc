from django.contrib import admin

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .models import IVEndpointCategory


class IVEndpointCategoryAdmin(TreeAdmin):
    form = movenodeform_factory(IVEndpointCategory)


admin.site.register(IVEndpointCategory, IVEndpointCategoryAdmin)
