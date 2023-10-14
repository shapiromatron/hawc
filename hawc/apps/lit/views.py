from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Q
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView

from ..assessment.constants import AssessmentViewPermissions
from ..assessment.models import Assessment
from ..common.crumbs import Breadcrumb
from ..common.helper import WebappConfig, tryParseInt
from ..common.views import (
    BaseCopyForm,
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseFilterList,
    BaseList,
    BaseUpdate,
    create_object_log,
)
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
        context["overview"] = models.Reference.objects.get_overview_details(self.assessment)
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
        kw.update(user=self.request.user, assessment=self.assessment)
        return kw

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["breadcrumbs"] = lit_overview_crumbs(
    #         self.request.user, self.assessment, "Copy search/import"
    #     )
    #     return context


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
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER
    paginate_by = 100

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("study")
            .prefetch_related("searches", "identifiers", "tags")
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
                appended_fields=["partially_tagged", "needs_tagging", "order_by"],
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
                    "authors",
                    "year",
                    "tags",
                    "include_descendants",
                    "anything_tagged",
                ],
                main_field="ref_search",
                appended_fields=["order_by"],
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
        for reference in references:
            reference["user_tags"] = ref_tags.get(reference["pk"])
        return WebappConfig(
            app="litStartup",
            page="startupTagReferences",
            data=dict(
                conflict_resolution=self.assessment.literature_settings.conflict_resolution,
                keywords=self.assessment.literature_settings.get_keyword_data(),
                instructions=self.assessment.literature_settings.screening_instructions,
                tags=models.ReferenceFilterTag.get_all_tags(self.assessment.id),
                refs=references,
                csrf=get_token(self.request),
            ),
        )


class ConflictResolution(BaseFilterList):
    template_name = "lit/conflict_resolution.html"
    parent_model = Assessment
    model = models.Reference
    filterset_class = filterset.ReferenceFilterSet
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER

    def get_filterset_form_kwargs(self):
        return dict(
            main_field="ref_search",
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

    paginate_by = 50

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                n_unapplied_reviews=Count("user_tags__user", filter=Q(user_tags__is_resolved=False))
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
    template_name = "lit/reference_visual.html"

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
            .prefetch_related("searches", "identifiers", "tags")
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
                tags=models.ReferenceFilterTag.get_all_tags(self.assessment.id),
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
    assessment_permission = AssessmentViewPermissions.PROJECT_MANAGER
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
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            assessment=self.assessment,
            reference_qs=models.Reference.objects.get_references_ready_for_import(self.assessment),
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
        context.update(
            breadcrumbs=lit_overview_crumbs(self.request.user, self.assessment, "Convert to study"),
            object_list=context["form"].fields["references"].queryset,
        )
        return context

    def get_success_url(self):
        return reverse_lazy("lit:ref_list_extract", args=[self.assessment.pk])


def _get_ref_app_startup(view, context) -> WebappConfig:
    return WebappConfig(
        app="litStartup",
        page="startupReferenceDetail",
        data={
            "tags": models.ReferenceFilterTag.get_all_tags(view.assessment.id),
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
        return context

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
    assessment_permission = AssessmentViewPermissions.PROJECT_MANAGER

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
    assessment_permission = AssessmentViewPermissions.PROJECT_MANAGER

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
    assessment_permission = AssessmentViewPermissions.PROJECT_MANAGER

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
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER

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
