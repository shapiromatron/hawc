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


@admin.register(models.Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_select_related = ("content_type",)
    list_display = ("id", "title", "attachment", "content_object", "publicly_available")
    list_display_links = ("id",)
    list_filter = ("publicly_available",)


class DatasetRevisionInline(admin.StackedInline):
    model = models.DatasetRevision


@admin.register(models.Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_select_related = ("assessment",)
    list_display = (
        "id",
        "assessment",
        "name",
        "description",
        "created",
        "last_updated",
    )
    list_display_links = ("id",)
    list_filter = (("assessment", admin.RelatedOnlyFieldListFilter),)
    inlines = [
        DatasetRevisionInline,
    ]


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


@admin.register(models.DSSTox)
class DSSXToxAdmin(admin.ModelAdmin):
    list_display = (
        "dtxsid",
        "get_casrns",
        "get_names",
        "get_assessments",
        "get_experiments",
        "get_ivchemicals",
    )
    search_fields = ("dtxsid", "content__casrn", "content__preferredName")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("assessments", "experiments", "ivchemicals")

    def get_ul(self, iterable, func):
        ul = ["<ul>"]
        for obj in iterable:
            ul.append(f"<li>{func(obj)}</li>")
        ul.append("</ul>")
        return format_html(" ".join(ul))

    def linked_name(self, obj):
        return f"<a href='{obj.get_absolute_url()}'>{obj.name}</a>"

    def get_casrns(self, obj):
        return obj.content["casrn"]

    get_casrns.short_description = "CASRN"
    get_casrns.allow_tags = True

    def get_names(self, obj):
        return obj.content["preferredName"]

    get_names.short_description = "Name"
    get_names.allow_tags = True

    def get_assessments(self, obj):
        return self.get_ul(obj.assessments.all(), self.linked_name)

    get_assessments.short_description = "Assessments"
    get_assessments.allow_tags = True

    def get_experiments(self, obj):
        return self.get_ul(obj.experiments.all(), self.linked_name)

    get_experiments.short_description = "Experiments"
    get_experiments.allow_tags = True

    def get_ivchemicals(self, obj):
        return self.get_ul(obj.ivchemicals.all(), self.linked_name)

    get_ivchemicals.short_description = "IVChemicals"
    get_ivchemicals.allow_tags = True
