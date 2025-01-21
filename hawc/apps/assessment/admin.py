from io import BytesIO

from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from ..animal.models import Endpoint
from ..common.admin import ReadOnlyAdmin
from . import forms, models


@admin.action(description="Clear cache for selected assessments")
def bust_cache(modeladmin, request, queryset):
    for assessment in queryset:
        assessment.bust_cache()
    message = f"Cache for {queryset.count()} assessment(s) busted!"
    modeladmin.message_user(request, message)


@admin.register(models.Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "__str__",
        "public_on",
        "hide_from_public_page",
        "editable",
        "get_managers",
        "get_team_members",
        "get_reviewers",
        "creator",
        "created",
        "last_updated",
    )
    list_filter = (
        "hide_from_public_page",
        "public_on",
        "editable",
        "created",
    )
    search_fields = (
        "name",
        "project_manager__last_name",
        "team_members__last_name",
        "reviewers__last_name",
        "creator__last_name",
    )
    actions = (bust_cache, "migrate_terms")
    form = forms.AssessmentAdminForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("creator").prefetch_related(
            "project_manager", "team_members", "reviewers"
        )

    def get_staff_ul(self, mgr):
        lis = format_html_join(
            "", "<li>{} {}</li>", ((u.first_name, u.last_name) for u in mgr.all())
        )
        return mark_safe(f"<ul>{lis}</ul>")

    @admin.display(description="Managers")
    def get_managers(self, obj):
        return self.get_staff_ul(obj.project_manager)

    @admin.display(description="Team")
    def get_team_members(self, obj):
        return self.get_staff_ul(obj.team_members)

    @admin.display(description="Reviewers")
    def get_reviewers(self, obj):
        return self.get_staff_ul(obj.reviewers)

    @admin.action(description="Migrate endpoint terms")
    def migrate_terms(self, request, queryset):
        # Action can only be run on one assessment at a time
        if queryset.count() != 1:
            self.message_user(
                request, "Select only one item to perform the action on.", level=messages.ERROR
            )
            return

        # Action can only be run on an assessment if controlled vocabulary is used
        assessment = queryset.first()
        if assessment.vocabulary is None:
            self.message_user(
                request, "Assessment has no controlled vocabulary.", level=messages.ERROR
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


@admin.register(models.AssessmentDetail)
class DetailsAdmin(admin.ModelAdmin):
    list_select_related = ("assessment",)
    list_filter = ("project_type",)
    list_display = ("id", "assessment", "project_type")


@admin.register(models.AssessmentValue)
class ValuesAdmin(admin.ModelAdmin):
    list_select_related = ("assessment",)
    list_display = ("id", "assessment", "value_type", "value", "comments")
    list_filter = ("assessment",)
    search_fields = (
        "assessment",
        "comments",
        "system",
        "basis",
        "tumor_type",
        "extrapolation_method",
        "evidence",
    )


@admin.register(models.Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_select_related = ("content_type",)
    list_display = ("id", "title", "attachment", "content_object", "publicly_available")
    list_display_links = ("id",)
    list_filter = ("publicly_available",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("content_object")


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
    search_fields = ("name",)
    list_display = (
        "name",
        "animal_dose_group_count",
        "epi_exposure_count",
        "invitro_experiment_count",
    )


@admin.register(models.Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("name",)
    search_fields = ("name",)


@admin.register(models.Strain)
class StrainAdmin(admin.ModelAdmin):
    list_select_related = ("species",)
    list_display = ("id", "name", "species")
    list_display_links = ("name",)
    list_filter = ("species",)
    search_fields = ("name",)


@admin.register(models.EffectTag)
class EffectTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "id")
    search_fields = ("name",)


@admin.register(models.TimeSpentEditing)
class TimeSpentEditingAdmin(ReadOnlyAdmin):
    list_display = (
        "id",
        "assessment",
        "content_type",
        "object_id",
        "seconds",
        "created",
    )
    list_select_related = ("assessment", "content_type")
    list_filter = (
        ("content_type", admin.RelatedOnlyFieldListFilter),
        ("assessment", admin.RelatedOnlyFieldListFilter),
    )


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


@admin.register(models.Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "object_id", "content_type", "created", "last_updated")
    readonly_fields = ("id", "object_id", "content_type", "created", "last_updated")
    search_fields = ("object_id", "message")


@admin.register(models.Log)
class LogAdmin(ReadOnlyAdmin):
    list_display = ("id", "created", "message", "assessment", "user")
    list_select_related = ("user", "assessment")
    list_filter = (
        ("assessment", admin.RelatedOnlyFieldListFilter),
        ("user", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("assessment__name", "message")
    readonly_fields = ("created",)


@admin.register(LogEntry)
class LogEntryAdmin(ReadOnlyAdmin):
    list_display = ("id", "action_time", "user", "content_type", "object_id", "action_flag")
    list_filter = (
        ("user", admin.RelatedOnlyFieldListFilter),
        ("content_type", admin.RelatedOnlyFieldListFilter),
    )
    list_select_related = ("user", "content_type")
    search_fields = ("object_id",)


@admin.register(ContentType)
class ContentTypeAdmin(ReadOnlyAdmin):
    list_display = ("id", "app_label", "model")
    list_filter = ("app_label",)
    search_fields = ("app_label", "model")


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
    list_filter = ("last_updated",)
    search_fields = ("dtxsid", "content__casrn", "content__preferredName")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("assessments", "experiments", "exposures", "ivchemicals")

    def get_ul(self, iterable, func):
        lis = "".join([(func(obj)) for obj in iterable])
        return format_html("<ul>{}</ul>", mark_safe(lis)) if lis else "-"

    def linked_name(self, obj):
        return format_html("<li><a href='{}'>{}</a></li>", obj.get_absolute_url(), obj.name)

    @admin.display(description="CASRN")
    def get_casrns(self, obj):
        return obj.content["casrn"]

    @admin.display(description="Name")
    def get_names(self, obj):
        return obj.content["preferredName"]

    @admin.display(description="Assessments")
    def get_assessments(self, obj):
        return self.get_ul(obj.assessments.all(), self.linked_name)

    @admin.display(description="Experiments")
    def get_experiments(self, obj):
        return self.get_ul(obj.experiments.all(), self.linked_name)

    @admin.display(description="Epi exposures")
    def get_exposures(self, obj):
        return self.get_ul(obj.exposures.all(), self.linked_name)

    @admin.display(description="IVChemicals")
    def get_ivchemicals(self, obj):
        return self.get_ul(obj.ivchemicals.all(), self.linked_name)


@admin.register(models.Content)
class ContentAdmin(VersionAdmin):
    list_display = (
        "content_type",
        "template_truncated",
        "created",
        "last_updated",
    )


@admin.register(models.Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "assessment",
        "published",
        "created",
        "last_updated",
    )
    readonly_fields = ("id",)
    search_fields = ("name",)
    readonly_fields = ("path", "depth", "numchild")


@admin.register(models.LabeledItem)
class LabeledItemAdmin(admin.ModelAdmin):
    list_select_related = ("content_type",)
    list_display = (
        "id",
        "label",
        "content_object",
        "created",
        "last_updated",
    )
    readonly_fields = ("id",)
    search_fields = (
        "label",
        "content_object",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("content_object")
