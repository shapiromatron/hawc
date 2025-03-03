from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Q, prefetch_related_objects
from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View

from ..assessment.constants import AssessmentViewPermissions
from ..assessment.models import Assessment
from ..common.crumbs import Breadcrumb
from ..common.helper import WebappConfig, try_parse_list_ints, tryParseInt
from ..common.htmx import HtmxView, HtmxViewSet, action, can_edit, can_view
from ..common.views import (
    BaseCopyForm,
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseFilterList,
    BaseList,
    BaseUpdate,
    MessageMixin,
    create_object_log,
    htmx_required,
)
from ..udf.cache import TagCache
from . import constants, filterset, forms, models


def lit_overview_breadcrumb(assessment) -> Breadcrumb:
    return Breadcrumb(name="Literature review", url=reverse("lit:overview", args=(assessment.id,)))


def lit_overview_crumbs(user, assessment: Assessment, name: str) -> list[Breadcrumb]:
    return Breadcrumb.build_crumbs(
        user, name, [Breadcrumb.from_object(assessment), lit_overview_breadcrumb(assessment)]
    )


class LitOverview(BaseList):
    parent_model = Assessment
    model = models.Search
    template_name = "lit/overview.html"
    breadcrumb_active_name = "Literature review"

    def get_queryset(self):
        return (
            super().get_queryset().filter(assessment=self.assessment).exclude(slug="manual-import")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["overview"], context["workflows"] = models.Reference.objects.get_overview_details(
            self.assessment
        )
        context["overview"]["my_reviews"] = (
            models.Reference.objects.filter(assessment=self.assessment)
            .filter(user_tags__user=self.request.user)
            .count()
            if self.request.user.is_authenticated
            else 0
        )
        context["manual_import"] = models.Search.objects.get_manually_added(self.assessment)
        if context["obj_perms"]["edit"]:
            context["need_import_count"] = models.Reference.objects.get_references_ready_for_import(
                self.assessment
            ).count()
        context["config"] = {
            "tags": models.ReferenceFilterTag.get_all_tags(self.assessment.id),
            "references": models.Reference.objects.tag_pairs(self.assessment.references.all()),
            "assessment_id": self.assessment.id,
            "referenceYearHistogramUrl": reverse(
                "lit:api:assessment-reference-year-histogram", args=(self.assessment.id,)
            ),
        }
        context["allow_ris"] = settings.HAWC_FEATURES.ALLOW_RIS_IMPORTS
        return context


class SearchCopyForm(BaseCopyForm):
    copy_model = models.Search
    form_class = forms.SearchCopyForm
    model = Assessment

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw.update(user=self.request.user)
        return kw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = lit_overview_crumbs(
            self.request.user, self.assessment, "Copy search/import"
        )
        return context


class SearchNew(BaseCreate):
    success_message = "Search created."
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.Search
    form_class = forms.SearchForm
    search_type = "Search"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = self.search_type
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # check if we have a template to use
        pk = tryParseInt(self.request.GET.get("initial"), -1)

        if pk > 0:
            obj = self.model.objects.filter(pk=pk).first()
            permitted_assesments = Assessment.objects.all().user_can_view(
                self.request.user, exclusion_id=self.assessment.pk
            )
            if obj and obj.assessment in permitted_assesments:
                kwargs["initial"] = model_to_dict(obj)

        return kwargs


class ImportNew(SearchNew):
    success_message = "Import created."
    form_class = forms.ImportForm
    search_type = "Import"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][-1].name = "Create import"
        return context


class ImportRISNew(ImportNew):
    form_class = forms.RisImportForm


class RISExportInstructions(TemplateView):
    template_name = "lit/ris_export_instructions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(self.request.user, "RIS instructions")
        return context


class SearchDetail(BaseDetail):
    model = models.Search

    def get_object(self, **kwargs):
        obj = get_object_or_404(
            models.Search,
            slug=self.kwargs.get(self.slug_url_kwarg),
            assessment=self.kwargs.get("pk"),
        )
        return super().get_object(object=obj)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        return context


class SearchUpdate(BaseUpdate):
    success_message = "Search updated."
    model = models.Search

    def get_form_class(self):
        if self.object.search_type == constants.SearchType.SEARCH:
            return forms.SearchForm
        elif self.object.search_type == constants.SearchType.IMPORT:
            if self.object.source == constants.ReferenceDatabase.RIS:
                return forms.RisImportForm
            else:
                return forms.ImportForm
        else:
            raise ValueError("Unknown search type")

    def get_object(self):
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        assessment = self.kwargs.get("pk", None)
        obj = get_object_or_404(models.Search, assessment=assessment, slug=slug)
        return super().get_object(object=obj)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = self.object.get_search_type_display()
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        return context


class SearchDelete(BaseDelete):
    success_message = "Search deleted."
    model = models.Search

    def get_object(self):
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        self.assessment = get_object_or_404(Assessment, pk=self.kwargs.get("pk"))
        obj = get_object_or_404(models.Search, assessment=self.assessment, slug=slug)
        return super().get_object(object=obj)

    def get_success_url(self):
        return reverse_lazy("lit:overview", kwargs={"pk": self.assessment.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        context["delete_notes"] = loader.render_to_string(
            "lit/_delete_search_warning.html", context, self.request
        )
        return context


class SearchQuery(BaseUpdate):
    model = models.Search
    form_class = forms.SearchForm
    http_method_names = ("get",)  # don't allow POST
    template_name = "lit/search_too_large.html"

    def get_object(self, **kwargs):
        obj = get_object_or_404(
            self.model,
            slug=self.kwargs.get(self.slug_url_kwarg),
            assessment=self.kwargs.get("pk"),
        )
        return super().get_object(object=obj)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.run_new_query()
        except models.TooManyPubMedResults as error:
            return self.render_to_response({"error": error})
        # attempt to extract DOIs from all references in search
        models.Reference.extract_dois(self.object.references.all())
        return HttpResponseRedirect(self.object.get_absolute_url())


class TagReferences(BaseFilterList):
    template_name = "lit/reference_tag.html"
    parent_model = Assessment
    model = models.Reference
    filterset_class = filterset.ReferenceFilterSet
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER_EDITABLE
    paginate_by = 100

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("study")
            .prefetch_related("searches", "identifiers", "tags", "saved_tag_contents__tag_binding")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            breadcrumbs=lit_overview_crumbs(self.request.user, self.assessment, "Update tags"),
        )
        return context

    def get_filterset_form_kwargs(self):
        conflict_resolution = self.assessment.literature_settings.conflict_resolution
        if conflict_resolution:
            return dict(
                main_field="ref_search",
                appended_fields=["partially_tagged", "needs_tagging", "workflow", "order_by"],
                dynamic_fields=[
                    "ref_search",
                    "needs_tagging",
                    "order_by",
                    "search",
                    "authors",
                    "year",
                    "partially_tagged",
                    "id",
                    "tags",
                    "include_descendants",
                    "anything_tagged",
                    "my_tags",
                    "include_mytag_descendants",
                    "anything_tagged_me",
                    "workflow",
                ],
                grid_layout={
                    "rows": [
                        {"columns": [{"width": 12}]},
                        {
                            "columns": [
                                {"width": 3},
                                {"width": 3},
                                {"width": 3},
                                {"width": 3},
                            ]
                        },
                        {
                            "columns": [
                                {
                                    "width": 6,
                                    "rows": [
                                        {
                                            "columns": [
                                                {"width": 12},
                                                {"width": 7},
                                                {"width": 5},
                                            ]
                                        }
                                    ],
                                },
                                {
                                    "width": 6,
                                    "rows": [
                                        {
                                            "columns": [
                                                {"width": 12},
                                                {"width": 7},
                                                {"width": 5},
                                            ]
                                        }
                                    ],
                                },
                            ]
                        },
                    ]
                },
            )
        else:
            return dict(
                dynamic_fields=[
                    "ref_search",
                    "search",
                    "id",
                    "order_by",
                    "workflow",
                    "authors",
                    "year",
                    "tags",
                    "include_descendants",
                    "anything_tagged",
                ],
                main_field="ref_search",
                appended_fields=["workflow", "order_by"],
                grid_layout={
                    "rows": [
                        {"columns": [{"width": 12}]},
                        {
                            "columns": [
                                {
                                    "width": 6,
                                    "rows": [
                                        {
                                            "columns": [
                                                {"width": 5},
                                                {"width": 7},
                                                {"width": 5},
                                                {"width": 7},
                                            ]
                                        }
                                    ],
                                },
                                {
                                    "width": 6,
                                    "rows": [
                                        {
                                            "columns": [
                                                {"width": 12},
                                                {"width": 6},
                                                {"width": 6},
                                            ]
                                        }
                                    ],
                                },
                            ]
                        },
                    ]
                },
            )

    def get_app_config(self, context) -> WebappConfig:
        references = [ref.to_dict() for ref in context["object_list"]]
        ref_tags = context["object_list"].unresolved_user_tags(user_id=self.request.user.id)
        tags = models.ReferenceFilterTag.get_all_tags(self.assessment.id)
        tag_names = models.ReferenceFilterTag.get_nested_tag_names(self.assessment.id)
        descendant_tags = models.ReferenceFilterTag.get_tree_descendants(tags)
        # dict[int,set] -> dict[int,list] so we can JSON-encode
        descendant_tags = {key: list(val) for key, val in descendant_tags.items()}
        for reference in references:
            reference["user_tags"] = ref_tags.get(reference["pk"])
            flattened_contents = {}
            # prepend UDF tag ID to name to prevent UDF name namespace conflicts
            # TODO - can this code + JS be removed the always list? it's needed for yes/no radio
            for tag_id, field in reference["tag_udf_contents"].items():
                for name, value in field.items():
                    flattened_contents[f"{tag_id}-{name}"] = (
                        value if isinstance(value, list) else [value]
                    )
            reference["tag_udf_contents"] = flattened_contents
        return WebappConfig(
            app="litStartup",
            page="startupTagReferences",
            data=dict(
                conflict_resolution=self.assessment.literature_settings.conflict_resolution,
                keywords=self.assessment.literature_settings.get_keyword_data(),
                instructions=self.assessment.literature_settings.screening_instructions,
                tags=tags,
                tag_names=tag_names,
                descendant_tags=descendant_tags,
                refs=references,
                csrf=get_token(self.request),
                udfs=TagCache.get_forms(self.assessment),
            ),
        )


@method_decorator(htmx_required, name="dispatch")
class BulkMerge(HtmxView):
    actions = {"preview", "merge"}

    def dispatch(self, request, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=kwargs.get("pk"))
        if not self.assessment.user_can_edit_object(request.user):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def index(self, request: HttpRequest, *args, **kwargs):
        form = forms.BulkMergeConflictsForm(assessment=self.assessment)
        context = dict(
            form=form, assessment=self.assessment, action="index", modal_id="bulk-merge-modal"
        )
        return render(request, "lit/components/bulk_merge_modal_content.html", context=context)

    def preview(self, request: HttpRequest, *args, **kwargs):
        queryset = (
            models.Reference.objects.filter(assessment=self.assessment)
            .order_by("-last_updated")
            .prefetch_related("identifiers", "tags", "user_tags__user", "user_tags__tags")
        )
        key = (
            f'{self.assessment.pk}-bulk-merge-tags-{"-".join(sorted(request.POST.getlist("tags")))}'
        )
        form = forms.BulkMergeConflictsForm(
            assessment=self.assessment, initial={**request.POST, "cache_key": key}
        )
        for field in "tags", "include_without_conflict":
            form.fields[field].disabled = True
        merge_result = queryset.merge_tag_conflicts(
            request.POST.getlist("tags"),
            request.user.id,
            request.POST.get("include_without_conflict", False),
            preview=True,
        )
        if merge_result["queryset"]:
            tags = models.ReferenceFilterTag.get_assessment_qs(self.assessment.id)
            models.Reference.annotate_tag_parents(
                merge_result["queryset"], tags, user_tags=True, check_bulk=True
            )
            cache.set(key, (merge_result["queryset"], request.POST), 60 * 30)  # 30 min

        context = dict(
            object_list=merge_result["queryset"],
            assessment=self.assessment,
            action="preview",
            message=merge_result["message"],
            form=form,
            cache_key=key,
        )
        return render(request, "lit/components/bulk_merge_modal_content.html", context=context)

    def merge(self, request: HttpRequest, *args, **kwargs):
        cache_key = request.POST.get("cache_key", "")
        queryset, data = cache.get(cache_key)
        assessment_ids = queryset.values_list("assessment_id", flat=True).distinct().order_by()
        reference_ids = list(queryset.values_list("id", flat=True))
        if not (self.assessment.id in assessment_ids and assessment_ids.count() == 1):
            raise PermissionDenied()
        form = forms.BulkMergeConflictsForm(assessment=self.assessment, initial=data)
        for field in "tags", "include_without_conflict":
            form.fields[field].disabled = True
        merge_result = queryset.merge_tag_conflicts(
            data.getlist("tags"),
            request.user.id,
            data.get("include_without_conflict", False),
            preview=False,
            cached=True,
        )
        final_qs = models.Reference.objects.filter(id__in=reference_ids).prefetch_related(
            "identifiers", "tags", "user_tags__user", "user_tags__tags"
        )
        tags = models.ReferenceFilterTag.get_assessment_qs(self.assessment.id)
        models.Reference.annotate_tag_parents(final_qs, tags, user_tags=True, check_bulk=False)
        context = dict(
            object_list=final_qs,
            assessment=self.assessment,
            action="merge",
            message=merge_result["message"],
            merged=merge_result["merged"],
            form=form,
        )
        return render(request, "lit/components/bulk_merge_modal_content.html", context=context)


class ConflictResolution(BaseFilterList):
    template_name = "lit/conflict_resolution.html"
    parent_model = Assessment
    model = models.Reference
    filterset_class = filterset.ReferenceFilterSet
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER_EDITABLE

    def get_filterset_form_kwargs(self):
        return dict(
            main_field="ref_search",
            appended_fields=["workflow"],
            dynamic_fields=[
                "id",
                "ref_search",
                "authors",
                "year",
                "tags",
                "include_descendants",
                "anything_tagged",
                "my_tags",
                "include_mytag_descendants",
                "anything_tagged_me",
                "workflow",
                "addition_tags",
                "include_additiontag_descendants",
                "deletion_tags",
                "include_deletiontag_descendants",
            ],
            grid_layout={
                "rows": [
                    {
                        "columns": [
                            {"width": 12},
                        ]
                    },
                    {
                        "columns": [
                            {"width": 3},
                            {"width": 6},
                            {"width": 3},
                        ]
                    },
                    {
                        "columns": [
                            {
                                "width": 3,
                                "rows": [
                                    {
                                        "columns": [
                                            {"width": 12},
                                            {"width": 12},
                                            {"width": 12},
                                        ]
                                    }
                                ],
                            },
                            {
                                "width": 3,
                                "rows": [
                                    {
                                        "columns": [
                                            {"width": 12},
                                            {"width": 12},
                                            {"width": 12},
                                        ]
                                    }
                                ],
                            },
                            {
                                "width": 3,
                                "rows": [
                                    {
                                        "columns": [
                                            {"width": 12},
                                            {"width": 12},
                                        ]
                                    }
                                ],
                            },
                            {
                                "width": 3,
                                "rows": [
                                    {
                                        "columns": [
                                            {"width": 12},
                                            {"width": 12},
                                        ]
                                    }
                                ],
                            },
                        ]
                    },
                ]
            },
        )

    paginate_by = 50

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                n_unapplied_reviews=Count(
                    "user_tags__user", filter=Q(user_tags__is_resolved=False), distinct=True
                )
            )
            .filter(n_unapplied_reviews__gt=1)
            .order_by("-last_updated")
            .prefetch_related("identifiers", "tags", "user_tags__user", "user_tags__tags")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tags = models.ReferenceFilterTag.get_assessment_qs(self.assessment.id)
        context.update(
            tags=tags,
            breadcrumbs=lit_overview_crumbs(
                self.request.user, self.assessment, "Resolve Tag Conflicts"
            ),
        )
        models.Reference.annotate_tag_parents(context["object_list"], tags)
        return context


def _get_reference_list(assessment, permissions, search=None) -> WebappConfig:
    qs = search.references.all() if search else assessment.references.all()
    return WebappConfig(
        app="litStartup",
        page="startupReferenceList",
        data=dict(
            assessment_id=assessment.id,
            search_id=search.id if search else None,
            tags=models.ReferenceFilterTag.get_all_tags(assessment.id),
            references=models.Reference.objects.tag_pairs(qs),
            canEdit=permissions["edit"],
            untaggedReferenceCount=qs.untagged().count(),
        ),
    )


class SearchRefList(BaseDetail):
    model = models.Search
    template_name = "lit/reference_list.html"

    def get_object(self, **kwargs):
        obj = get_object_or_404(
            models.Search,
            slug=self.kwargs.get(self.slug_url_kwarg),
            assessment=self.kwargs.get("pk"),
        )
        return super().get_object(object=obj)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        context["breadcrumbs"].append(Breadcrumb(name="References"))
        return context

    def get_app_config(self, context) -> WebappConfig:
        return _get_reference_list(self.assessment, context["obj_perms"], self.object)


def _get_viz_app_startup(view, context, search=None) -> WebappConfig:
    title = f'"{search}" Literature Tagtree' if search else f"{view.assessment}: Literature Tagtree"
    qs = search.references.all() if search else view.assessment.references.all()
    return WebappConfig(
        app="litStartup",
        page="startupTagTreeViz",
        data=dict(
            can_edit=context["obj_perms"]["edit"],
            assessment_id=view.assessment.id,
            assessment_name=str(view.assessment),
            search_id=search.id if search else None,
            tags=models.ReferenceFilterTag.get_all_tags(view.assessment.id),
            title=title,
            references=models.Reference.objects.tag_pairs(qs),
        ),
    )


class SearchTagsVisualization(BaseDetail):
    model = models.Search
    template_name = "lit/reference_search_visual.html"

    def get_object(self, **kwargs):
        obj = get_object_or_404(
            models.Search,
            slug=self.kwargs.get(self.slug_url_kwarg),
            assessment=self.kwargs.get("pk"),
        )
        return super().get_object(object=obj)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        context["breadcrumbs"].append(Breadcrumb(name="Visualization"))
        return context

    def get_app_config(self, context) -> WebappConfig:
        return _get_viz_app_startup(self, context, search=self.object)


class RefList(BaseList):
    parent_model = Assessment
    model = models.Reference

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        return context

    def get_app_config(self, context) -> WebappConfig:
        return _get_reference_list(self.assessment, context["obj_perms"])


def _get_tag_binding_contents(assessment, reference_list):
    # Get assessment tags and UDF data for all consensus tags in a reference list
    tags = models.ReferenceFilterTag.get_all_tags(assessment.id)
    tag_names = models.ReferenceFilterTag.get_nested_tag_names(assessment.id)
    descendant_tags = models.ReferenceFilterTag.get_tree_descendants(tags)
    descendant_tags = {key: list(val) for key, val in descendant_tags.items()}
    tag_binding_contents = {}
    for reference in reference_list:
        tag_binding_contents[reference.pk] = [
            {
                "tag_name": tag_names[tag_content.tag_binding.tag.pk],
                "tag_pk": tag_content.tag_binding.tag.pk,
                "udf_content": tag_content.get_content_as_list(),
                "udf_name": tag_content.tag_binding.form.name,
            }
            for tag_content in reference.saved_tag_contents.all()
            if set(descendant_tags.get(tag_content.tag_binding.tag.pk, [])).intersection(
                set(reference.tags.values_list("pk", flat=True))
            )
        ]
    return {
        "tags": tags,
        "tag_binding_contents": tag_binding_contents,
    }


class RefFilterList(BaseFilterList):
    template_name = "lit/reference_search.html"
    breadcrumb_active_name = "Reference search"
    parent_model = Assessment
    model = models.Reference
    filterset_class = filterset.ReferenceFilterSet

    def get_filterset_form_kwargs(self):
        return dict(
            main_field="ref_search",
            appended_fields=["order_by", "paginate_by"],
            dynamic_fields=[
                "id",
                "db_id",
                "search",
                "authors",
                "year",
                "ref_search",
                "journal",
                "order_by",
                "paginate_by",
                "tags",
                "include_descendants",
                "anything_tagged",
            ],
            grid_layout={
                "rows": [
                    {"columns": [{"width": 12}]},
                    {
                        "columns": [
                            {
                                "width": 6,
                                "rows": [
                                    {
                                        "columns": [
                                            {"width": 6},
                                            {"width": 6},
                                            {"width": 6},
                                            {"width": 6},
                                            {"width": 6},
                                            {"width": 6},
                                        ]
                                    },
                                ],
                            },
                            {
                                "width": 6,
                                "rows": [
                                    {
                                        "columns": [
                                            {"width": 12},
                                            {"width": 6},
                                            {"width": 6},
                                        ]
                                    }
                                ],
                            },
                        ]
                    },
                ]
            },
        )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("study")
            .prefetch_related("searches", "identifiers", "tags", "saved_tag_contents")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="litStartup",
            page="startupReferenceTable",
            data=dict(
                **_get_tag_binding_contents(self.assessment, context["object_list"]),
                references=[ref.to_dict() for ref in context["object_list"]],
            ),
        )


class RefUploadExcel(BaseUpdate):
    """
    Upload Excel files and update reference details.
    """

    model = Assessment
    template_name = "lit/reference_upload_excel.html"
    form_class = forms.ReferenceExcelUploadForm
    assessment_permission = AssessmentViewPermissions.PROJECT_MANAGER_EDITABLE
    success_message = "Reference full text URLs updated."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["assessment"] = self.assessment
        return kwargs

    def create_log(self, obj):
        create_object_log(
            "Reference URLs bulk updated", self.assessment, self.assessment.id, self.request.user.id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = lit_overview_crumbs(
            self.request.user, self.assessment, "Update full text URLs"
        )
        return context

    def get_success_url(self):
        return reverse_lazy("lit:overview", args=[self.assessment.pk])


class RefListExtract(BaseUpdate):
    template_name = "lit/reference_extract_list.html"
    breadcrumb_active_name = "Prepare for extraction"
    model = Assessment
    form_class = forms.BulkReferenceStudyExtractForm
    success_message = "Selected references were successfully converted to studies."
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER_EDITABLE

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            assessment=self.assessment,
            reference_qs=models.Reference.objects.get_references_ready_for_import(self.assessment)
            .select_related("study")
            .prefetch_related("searches", "identifiers", "tags"),
        )
        return kwargs

    def create_log(self, obj):
        create_object_log(
            "Reference converted to study",
            self.assessment,
            self.assessment.id,
            self.request.user.id,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tags = models.ReferenceFilterTag.get_assessment_qs(self.assessment.id)
        context.update(
            breadcrumbs=lit_overview_crumbs(self.request.user, self.assessment, "Convert to study"),
            object_list=context["form"].fields["references"].queryset,
        )
        models.Reference.annotate_tag_parents(context["object_list"], tags, user_tags=False)
        return context

    def get_success_url(self):
        return reverse_lazy("lit:ref_list_extract", args=[self.assessment.pk])


def _get_ref_app_startup(view, context) -> WebappConfig:
    return WebappConfig(
        app="litStartup",
        page="startupReferenceDetail",
        data={
            **_get_tag_binding_contents(view.assessment, [view.object]),
            "reference": view.object.to_dict(),
            "canEdit": context["obj_perms"]["edit"],
        },
    )


class RefDetail(BaseDetail):
    model = models.Reference

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        return context

    def get_app_config(self, context) -> WebappConfig:
        return _get_ref_app_startup(self, context)


class ReferenceTagStatus(BaseDetail):
    template_name = "lit/reference_tag_status.html"
    model = models.Reference
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("assessment")
            .prefetch_related("identifiers", "tags", "user_tags__tags", "user_tags__user")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = lit_overview_crumbs(
            self.request.user, self.assessment, "Tag status"
        )
        context["breadcrumbs"].insert(3, Breadcrumb.from_object(self.object))
        tags = models.ReferenceFilterTag.get_assessment_qs(self.assessment.id)
        models.Reference.annotate_tag_parents([self.object], tags)
        return context


class UserTagList(ConflictResolution):
    template_name = "lit/reference_user_tags.html"

    def get_queryset(self):
        return (
            self.filterset.qs.filter(user_tags__gt=0)
            .order_by("-last_updated")
            .prefetch_related("identifiers", "tags", "user_tags__user", "user_tags__tags")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = lit_overview_crumbs(
            self.request.user, self.assessment, "Reference User Tags"
        )
        context["header"] = "Reference User Tags"
        return context


class RefEdit(BaseUpdate):
    success_message = "Reference updated."
    model = models.Reference
    form_class = forms.ReferenceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        return context


class RefDelete(BaseDelete):
    success_message = "Reference deleted."
    model = models.Reference

    def get_success_url(self):
        return reverse_lazy("lit:overview", args=(self.assessment.pk,))

    def check_delete(self):
        if self.object.has_study:
            raise PermissionDenied("Cannot delete - object has related study")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        return context

    def get_app_config(self, context) -> WebappConfig:
        return _get_ref_app_startup(self, context)


class RefVisualization(BaseDetail):
    model = Assessment
    template_name = "lit/reference_visual.html"
    breadcrumb_active_name = "Visualization"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        self.set_venn_data(context)
        return context

    def set_venn_data(self, context: dict):
        tags = models.ReferenceFilterTag.get_assessment_qs(self.assessment.id)
        form = forms.VennForm(
            assessment=self.assessment,
            tags=tags,
            data=self.request.GET if self.request.GET else None,
            initial=dict(tag1=tags[0], tag2=tags[1]),
        )
        context.update(
            venn=dict(
                form=form,
                app=WebappConfig(
                    app="litStartup",
                    page="startupVenn",
                    data={
                        "sets": form.get_venn() if form.is_valid() else [],
                        "csrf": get_token(self.request),
                        "url": reverse("lit:interactive", args=(self.assessment.id,))
                        + "?action=venn_reference_list",
                    },
                ).model_dump(),
            )
        )

    def get_app_config(self, context) -> WebappConfig:
        return _get_viz_app_startup(self, context)


class TagsUpdate(BaseDetail):
    """
    Update tags for an assessment. Note that right now, only project managers
    of the assessment can update tags. (we use the Assessment as the model in an
    update-view, which only project-managers have permission to do-so).
    """

    model = Assessment
    template_name = "lit/tags_update.html"
    assessment_permission = AssessmentViewPermissions.PROJECT_MANAGER_EDITABLE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            breadcrumbs=lit_overview_crumbs(self.request.user, self.assessment, "Update tags"),
            lit_assesment_update_url=self.assessment.literature_settings.get_update_url(),
        )
        return context

    def get_app_config(self, context) -> WebappConfig:
        overview = reverse("lit:overview", args=(self.assessment.pk,))
        api_root = reverse("lit:api:tags-list")
        return WebappConfig(
            app="nestedTagEditorStartup",
            data=dict(
                assessment_id=self.assessment.id,
                references=models.Reference.objects.tag_pairs(self.assessment.references.all()),
                base_url=api_root,
                list_url=f"{api_root}?assessment_id={self.assessment.id}",
                csrf=get_token(self.request),
                host=self.request.get_host(),
                title=f"Reference tags for {self.assessment}",
                extraHelpHtml=f"""
                        Edit tags which can be applied to literature for this assessment. If
                        extracting data, all references marked with a tag in the "Inclusion"
                        category will be labeled as ready for data-extraction on the assessment
                        literature review page (<a href="{overview}">here</a>).<br/><br/>""",
                btnLabel="Add new tag",
            ),
        )


class LiteratureAssessmentUpdate(BaseUpdate):
    success_message = "Literature assessment settings updated."
    model = models.LiteratureAssessment
    form_class = forms.LiteratureAssessmentForm
    assessment_permission = AssessmentViewPermissions.PROJECT_MANAGER_EDITABLE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][2] = lit_overview_breadcrumb(self.assessment)
        return context

    def get_success_url(self):
        return reverse_lazy("lit:overview", args=(self.assessment.id,))


class TagsCopy(BaseUpdate):
    """
    Remove exiting tags and copy all tags from a separate assessment.
    """

    model = Assessment
    template_name = "lit/tags_copy.html"
    form_class = forms.TagsCopyForm
    success_message = "Literature tags for this assessment have been updated"
    assessment_permission = AssessmentViewPermissions.PROJECT_MANAGER_EDITABLE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = lit_overview_crumbs(
            self.request.user, self.assessment, "Copy tags"
        )
        return context

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw.update(user=self.request.user, assessment=self.assessment)
        kw.pop("instance")
        return kw

    @transaction.atomic
    def form_valid(self, form):
        url = reverse("lit:tags_update", kwargs={"pk": self.assessment.pk})
        create_object_log("Bulk tag copy", self.object, self.object.id, self.request.user.id)
        form.copy_tags()
        return HttpResponseRedirect(url)


class BulkTagReferences(BaseDetail):
    model = Assessment
    template_name = "lit/bulk_tag_references.html"
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER_EDITABLE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = lit_overview_crumbs(
            self.request.user, self.assessment, "Bulk tag references"
        )
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="litStartup",
            page="startupBulkTagReferences",
            data={"assessment_id": self.assessment.id, "csrf": get_token(self.request)},
        )


class Workflows(BaseList):
    parent_model = Assessment
    model = models.Workflow
    breadcrumb_active_name = "Workflows"
    template_name = "lit/workflows.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["breadcrumbs"] = lit_overview_crumbs(
            self.request.user, self.assessment, "Workflows"
        )
        return context

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(assessment=self.assessment)
            .prefetch_related("admission_tags", "removal_tags")
            .order_by("-created")
        )
        tags = models.ReferenceFilterTag.get_assessment_qs(self.assessment.id)
        models.Workflow.annotate_tag_parents(queryset, tags)
        return queryset


class WorkflowViewSet(HtmxViewSet):
    actions = {"create", "read", "update", "delete"}
    parent_model = Assessment
    model = models.Workflow

    form_fragment = "lit/fragments/workflow_edit_row.html"
    detail_fragment = "lit/fragments/workflow_row.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        tags = models.ReferenceFilterTag.get_assessment_qs(request.item.assessment.id)
        prefetch_related_objects([request.item.object], "admission_tags", "removal_tags")
        models.Workflow.annotate_tag_parents([request.item.object], tags)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        form_data = request.POST if request.method == "POST" else None
        form = forms.WorkflowForm(data=form_data, parent=request.item.parent)
        context = self.get_context_data(form=form)
        if request.method == "POST" and form.is_valid():
            self.perform_create(request.item, form)
            template = self.detail_fragment
            context.update(object=request.item.object)
            tags = models.ReferenceFilterTag.get_assessment_qs(request.item.assessment.id)
            prefetch_related_objects([request.item.object], "admission_tags", "removal_tags")
            models.Workflow.annotate_tag_parents([request.item.object], tags)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        form_data = request.POST if request.method == "POST" else None
        form = forms.WorkflowForm(data=form_data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
            tags = models.ReferenceFilterTag.get_assessment_qs(request.item.assessment.id)
            prefetch_related_objects([request.item.object], "admission_tags", "removal_tags")
            models.Workflow.annotate_tag_parents([request.item.object], tags)
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            self.perform_delete(request.item)
            return self.str_response()
        form = forms.WorkflowForm(data=None, instance=request.item.object)
        context = self.get_context_data(form=form)
        return render(request, self.form_fragment, context)


class AssessmentInteractive(HtmxView):
    actions = {"venn_reference_list"}

    def dispatch(self, request, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=kwargs.get("pk"))
        if not self.assessment.user_can_view_object(request.user):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def venn_reference_list(self, request, *args, **kwargs):
        ids = try_parse_list_ints(request.POST.get("ids"))
        context = {
            "qs": models.Reference.objects.assessment_qs(self.assessment.id).filter(id__in=ids)
        }
        return render(request, "lit/components/venn_reference_list.html", context=context)


@method_decorator(staff_member_required, name="dispatch")
class DuplicateResolution(BaseList):
    parent_model = Assessment
    model = models.DuplicateCandidateGroup
    template_name = "lit/duplicate_resolution.html"
    breadcrumb_active_name = "Duplicate resolution"
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER

    paginate_by = 10

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(assessment=self.assessment)
            .filter(resolution=constants.DuplicateResolution.UNRESOLVED)
            .prefetch_related("candidates", "candidates__identifiers", "candidates__tags")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = lit_overview_crumbs(
            self.request.user, self.assessment, "Duplicate resolution"
        )
        return context


@method_decorator(staff_member_required, name="dispatch")
class ResolvedDuplicates(BaseFilterList):
    parent_model = Assessment
    model = models.DuplicateCandidateGroup
    filterset_class = filterset.DuplicateCandidateGroupFilterSet
    template_name = "lit/resolved_duplicates.html"
    breadcrumb_active_name = "Resolved duplicates"
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER

    paginate_by = 10

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(assessment=self.assessment)
            .exclude(resolution=constants.DuplicateResolution.UNRESOLVED)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = lit_overview_crumbs(
            self.request.user, self.assessment, "Resolved duplicates"
        )
        context["resolution_state"] = constants.DuplicateResolution
        return context


@method_decorator(staff_member_required, name="dispatch")
class IdentifyDuplicates(MessageMixin, View):
    success_message = "Duplicate identification requested."

    def get(self, request, *args, **kwargs):
        assessment = get_object_or_404(Assessment, pk=kwargs["pk"])
        if not assessment.user_can_edit_object(request.user):
            raise PermissionDenied()
        url = reverse("lit:duplicate-resolution", args=(assessment.pk,))
        models.DuplicateCandidateGroup.create_duplicate_candidate_groups(assessment.pk)
        self.send_message()
        return HttpResponseRedirect(url)
