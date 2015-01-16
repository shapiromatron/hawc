from django.db.models import TextField
from django.contrib import admin

from pagedown.widgets import AdminPagedownWidget

from . import models


#http://www.b-list.org/weblog/2008/dec/24/admin/
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'get_managers', 'get_team_members', 'get_reviewers')
    list_per_page = 10
    search_fields = ('name', 'project_manager__last_name', 'team_members__last_name', 'reviewers__last_name')
    list_filter = ('editable', 'public', )

    def queryset(self, request):
        qs = super(AssessmentAdmin, self).queryset(request)
        return qs.prefetch_related('project_manager', 'team_members', 'reviewers')

    def get_staff_ul(self, mgr):
        ul = ["<ul>"]
        for user in mgr.all():
            ul.append(u"<li>{} {}</li>".format(user.first_name, user.last_name))

        ul.append("</ul>")
        return u" ".join(ul)

    def get_managers(self, obj):
        return self.get_staff_ul(obj.project_manager)

    def get_team_members(self, obj):
        return self.get_staff_ul(obj.team_members)

    def get_reviewers(self, obj):
        return self.get_staff_ul(obj.reviewers)

    get_managers.short_description = 'Managers'
    get_managers.allow_tags = True

    get_team_members.short_description = 'Team'
    get_team_members.allow_tags = True

    get_reviewers.short_description = 'Reviewers'
    get_reviewers.allow_tags = True

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
