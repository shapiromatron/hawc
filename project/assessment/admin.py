from django.db.models import TextField
from django.contrib import admin

from pagedown.widgets import AdminPagedownWidget

from . import models


#http://www.b-list.org/weblog/2008/dec/24/admin/
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'year', 'name', 'version')


class EffectTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'id')


class ChangeLogAdmin(admin.ModelAdmin):
    # list options
    list_display = ('__unicode__', 'header', 'view_on_site')

    def view_on_site(self, obj):
        return '<a target="_blank" href="{0}">View</a>'.format(obj.get_absolute_url())

    view_on_site.allow_tags = True

    # form options
    formfield_overrides = {
        TextField: {'widget': AdminPagedownWidget },
    }

    prepopulated_fields = {"slug": ("date", "name")}


class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'get_report_type_display', 'description', 'created', 'last_updated')


admin.site.register(models.Assessment, AssessmentAdmin)
admin.site.register(models.EffectTag, EffectTagAdmin)
admin.site.register(models.ChangeLog, ChangeLogAdmin)
admin.site.register(models.ReportTemplate, ReportTemplateAdmin)
