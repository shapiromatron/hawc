from django.contrib import admin
from django.utils.html import format_html

from . import models


def bust_cache(modeladmin, request, queryset):
    for assessment in queryset:
        assessment.bust_cache()
    message = f"Cache for {queryset.count()} assessment(s) busted!"
    modeladmin.message_user(request, message)


bust_cache.short_description = "Clear cache for selected assessments"


@admin.register(models.Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("__str__", "get_managers", "get_team_members", "get_reviewers")
    list_per_page = 10
    list_filter = (
        "editable",
        "public",
    )

    search_fields = (
        "name",
        "project_manager__last_name",
        "team_members__last_name",
        "reviewers__last_name",
    )

    actions = (bust_cache,)

    def queryset(self, request):
        qs = super().queryset(request)
        return qs.prefetch_related("project_manager", "team_members", "reviewers")

    def get_staff_ul(self, mgr):
        ul = ["<ul>"]
        for user in mgr.all():
            ul.append(f"<li>{user.first_name} {user.last_name}</li>")

        ul.append("</ul>")
        return format_html(" ".join(ul))

    def get_managers(self, obj):
        return self.get_staff_ul(obj.project_manager)

    def get_team_members(self, obj):
        return self.get_staff_ul(obj.team_members)

    def get_reviewers(self, obj):
        return self.get_staff_ul(obj.reviewers)

    get_managers.short_description = "Managers"
    get_managers.allow_tags = True

    get_team_members.short_description = "Team"
    get_team_members.allow_tags = True

    get_reviewers.short_description = "Reviewers"
    get_reviewers.allow_tags = True


@admin.register(models.DoseUnits)
class DoseUnitsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "animal_dose_group_count",
        "epi_exposure_count",
        "invitro_experiment_count",
    )


@admin.register(models.Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    list_display_links = ("name",)


@admin.register(models.Strain)
class StrainAdmin(admin.ModelAdmin):
    list_select_related = ("species",)
    list_display = ("id", "name", "species")
    list_display_links = ("name",)
    list_filter = ("species",)


@admin.register(models.EffectTag)
class EffectTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "id")
    search_fields = ("name",)


@admin.register(models.TimeSpentEditing)
class TimeSpentEditingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "seconds",
        "assessment",
        "content_type",
        "object_id",
        "content_object",
        "created",
    )
    search_fields = (
        "assessment",
        "content_type",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display_links = []
