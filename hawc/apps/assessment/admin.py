from datetime import timedelta
from io import BytesIO

from django.apps import apps
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html
from reversion.admin import VersionAdmin

from ..animal.models import Endpoint
from . import models


def bust_cache(modeladmin, request, queryset):
    for assessment in queryset:
        assessment.bust_cache()
    message = f"Cache for {queryset.count()} assessment(s) busted!"
    modeladmin.message_user(request, message)


bust_cache.short_description = "Clear cache for selected assessments"


@admin.register(models.Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("__str__", "creator", "get_managers", "get_team_members", "get_reviewers")
    list_per_page = 10
    list_filter = (
        "editable",
        "public",
        ("creator", admin.RelatedOnlyFieldListFilter),
    )

    search_fields = (
        "name",
        "project_manager__last_name",
        "team_members__last_name",
        "reviewers__last_name",
    )

    actions = (bust_cache, "migrate_terms", "delete_orphan_tags")

    def queryset(self, request):
        qs = super().queryset(request)
        return qs.prefetch_related("project_manager", "team_members", "reviewers")

    def delete_orphan_tags(self, request, queryset):
        # Action can only be run on one assessment at a time
        if queryset.count() != 1:
            self.message_user(
                request, f"Select only one item to perform the action on.", level=messages.WARNING
            )
            return
        assessment = queryset.first()
        # delete tags that are not in the assessment tag tree
        ReferenceTags = apps.get_model("lit", "ReferenceTags")
        deleted, log_id = ReferenceTags.objects.delete_orphan_tags(assessment.id)
        # send a message with number deleted & log id
        tags = ReferenceTags.objects.get_assessment_qs(assessment.id)
        self.message_user(
            request,
            f"Deleted {deleted} of {deleted+tags.count()} reference tags. Details can be found at Log {log_id}.",
        )

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

    delete_orphan_tags.short_description = "Delete orphaned tags"

    get_managers.short_description = "Managers"
    get_managers.allow_tags = True

    get_team_members.short_description = "Team"
    get_team_members.allow_tags = True

    get_reviewers.short_description = "Reviewers"
    get_reviewers.allow_tags = True

    def migrate_terms(self, request, queryset):
        # Action can only be run on one assessment at a time
        if queryset.count() != 1:
            self.message_user(
                request, f"Select only one item to perform the action on.", level=messages.ERROR
            )
            return

        # Action can only be run on an assessment if controlled vocabulary is used
        assessment = queryset.first()
        if assessment.vocabulary is None:
            self.message_user(
                request, f"Assessment has no controlled vocabulary.", level=messages.ERROR
            )
            return

        df = Endpoint.objects.migrate_terms(assessment)

        # Writes an excel report of applied terms on the endpoints
        f = BytesIO()
        df.to_excel(f, index=False)

        response = HttpResponse(
            f.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        fn = f"attachment; filename=assessment-{assessment.id}-term-migration.xlsx"
        response["Content-Disposition"] = fn

        return response

    migrate_terms.short_description = "Migrate endpoint terms"


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
    inlines = [DatasetRevisionInline]
    readonly_fields = ("assessment_id", "assessment")


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


@admin.register(models.Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "task_id",
        "assessment",
        "job",
        "kwargs",
        "status",
    )
    search_fields = ("task_id",)
    list_filter = ("status",)
    readonly_fields = ("result",)


@admin.register(models.Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ("assessment", "message", "created", "last_updated")
    search_fields = ("assessment__name", "message")
    actions = ("delete_gt_year",)

    def delete_gt_year(self, request, queryset):
        # delete where "last_updated" > 1 year old
        year_old = timezone.now() - timedelta(days=365)
        deleted, _ = queryset.filter(last_updated__lte=year_old).delete()
        # send a message with number deleted
        self.message_user(request, f"{deleted} of {queryset.count()} selected logs deleted.")

    delete_gt_year.short_description = "Delete 1 year or older"


@admin.register(models.Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("subject", "published", "created", "last_updated")
    list_filter = ("published",)
    search_fields = ("subject", "content")
    readonly_fields = ("rendered_content",)


@admin.register(models.DSSTox)
class DSSXToxAdmin(admin.ModelAdmin):
    list_display = (
        "dtxsid",
        "get_casrns",
        "get_names",
        "get_assessments",
        "get_experiments",
        "get_exposures",
        "get_ivchemicals",
    )
    search_fields = ("dtxsid", "content__casrn", "content__preferredName")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("assessments", "experiments", "exposures", "ivchemicals")

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

    def get_exposures(self, obj):
        return self.get_ul(obj.exposures.all(), self.linked_name)

    get_exposures.short_description = "Epi exposures"
    get_exposures.allow_tags = True

    def get_ivchemicals(self, obj):
        return self.get_ul(obj.ivchemicals.all(), self.linked_name)

    get_ivchemicals.short_description = "IVChemicals"
    get_ivchemicals.allow_tags = True


@admin.register(models.Content)
class ContentAdmin(VersionAdmin):
    list_display = (
        "content_type",
        "template_truncated",
        "created",
        "last_updated",
    )
