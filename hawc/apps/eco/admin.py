from django.contrib import admin

from . import models

admin.site.register(models.Reference)
admin.site.register(models.Metadata)
admin.site.register(models.Cause)
admin.site.register(models.Effect)
admin.site.register(models.Quantitative)
admin.site.register(models.State)
admin.site.register(models.Ecoregion)
admin.site.register(models.Climate)
