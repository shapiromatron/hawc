from django.contrib import admin

from . import models


class CustomDataExtractionInline(admin.TabularInline):
    model = models.CustomDataExtraction
    extra = 0


admin.site.register(models.CustomDataExtraction)
