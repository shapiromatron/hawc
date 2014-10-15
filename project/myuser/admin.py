from django.contrib import admin

from . import models


class HAWCUserAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'email', 'is_active',  'is_staff', 'date_joined')
    list_filter = ('date_joined', )
    ordering = ('-date_joined', )

admin.site.register(models.HAWCUser, HAWCUserAdmin)
