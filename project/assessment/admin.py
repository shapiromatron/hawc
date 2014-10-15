from django.contrib import admin

from . import models


#http://www.b-list.org/weblog/2008/dec/24/admin/
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'year', 'name', 'version')


class EffectTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'pk')


admin.site.register(models.Assessment, AssessmentAdmin)
admin.site.register(models.EffectTag, EffectTagAdmin)
