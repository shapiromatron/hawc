from django.contrib import admin

from . import models


class UserDefinedFormInline(admin.TabularInline):
    model = models.UserDefinedForm
    extra = 0


class ModelBindingInline(admin.TabularInline):
    model = models.ModelBinding
    extra = 0


class TagBindingInline(admin.TabularInline):
    model = models.TagBinding
    extra = 0


admin.site.register(models.UserDefinedForm)
admin.site.register(models.ModelBinding)
admin.site.register(models.TagBinding)
