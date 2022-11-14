import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormView

from ..assessment.models import Assessment
from ..common.crumbs import Breadcrumb
from ..common.filterset import dynamic_filterset
from ..common.helper import WebappConfig, listToUl, tryParseInt
from ..common.views import (
    AssessmentPermissionsMixin,
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseFilterList,
    BaseList,
    BaseUpdate,
    MessageMixin,
    ProjectManagerOrHigherMixin,
    TeamMemberOrHigherMixin,
    WebappMixin,
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
        return self.model.objects.filter(assessment=self.assessment).exclude(slug="manual-import")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["overview"] = models.Reference.objects.get_overview_details(self.assessment)
        context["manual_import"] = models.Search.objects.get_manually_added(self.assessment)
        if context["obj_perms"]["edit"]:
            context["need_import_count"] = models.Reference.objects.get_references_ready_for_import(
                self.assessment
            ).count()
        context["can_topic_model"] = self.assessment.literature_settings.can_topic_model()
        context["config"] = {
            "tags": models.ReferenceFilterTag.get_all_tags(self.assessment.id),
            "assessment_id": self.assessment.id,
            "referenceYearHistogramUrl": reverse(
                "lit:api:assessment-reference-year-histogram", args=(self.assessment.id,)
            ),
        }
        context["allow_ris"] = settings.HAWC_FEATURES.ALLOW_RIS_IMPORTS
        return context


class SearchCopyAsNewSelector(TeamMemberOrHigherMixin, FormView):
    """
    Select an existing search and copy-as-new
    """

    template_name = "lit/search_copy_selector.html"
    form_class = forms.SearchSelectorForm

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(Assessment, pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = lit_overview_crumbs(
            self.request.user, self.assessment, "Copy literature search or import"
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["assessment"] = self.assessment
        return kwargs

    def form_valid(self, form):
        return HttpResponseRedirect(form.get_success_url())


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
            permitted_assesments = Assessment.objects.get_viewable_assessments(
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


class TagReferences(WebappMixin, TeamMemberOrHigherMixin, FormView):
    """
    Abstract base-class to tag references, using various methods to get instance.
    """

    model = Assessment
    form_class = forms.TagReferenceForm
    template_name = "lit/reference_tag.html"

    def get_ref_qs_filters(self) -> dict:
        raise NotImplementedError("Subclass requires implementation")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            breadcrumbs=lit_overview_crumbs(self.request.user, self.assessment, "CHANGE"),
        )
        return context

    def get_app_config(self, context) -> WebappConfig:
        if hasattr(self, "qs_reference"):
            refs = self.qs_reference
        else:
            refs = refs = models.Reference.objects.filter(**self.get_ref_qs_filters()).distinct()
        refs = refs.prefetch_related("searches", "identifiers", "tags")
        return WebappConfig(
            app="litStartup",
            page="startupTagReferences",
            data=dict(
                tags=models.ReferenceFilterTag.get_all_tags(self.assessment.id),
                refs=[ref.to_dict() for ref in refs],
                csrf=get_token(self.request),
            ),
        )


class TagBySearch(TagReferences):
    """
    Edit tags for a single Search.
    """

    model = models.Search

    def get_assessment(self, request, *args, **kwargs):
        self.object = get_object_or_404(
            self.model, slug=self.kwargs.get("slug"), assessment=self.kwargs.get("pk")
        )
        return self.object.get_assessment()

    def get_ref_qs_filters(self):
        return dict(searches=self.object)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][3] = Breadcrumb.from_object(self.object)
        context["breadcrumbs"].append(Breadcrumb(name="Update tags"))
        return context


class TagByReference(TagReferences):
    """
    Edit tags for on a single reference.
    """

    model = models.Reference

    def get_assessment(self, request, *args, **kwargs):
        self.object = get_object_or_404(self.model, pk=self.kwargs.get("pk"))
        return self.object.get_assessment()

    def get_ref_qs_filters(self):
        return dict(pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][3] = Breadcrumb.from_object(self.object)
        context["breadcrumbs"].append(Breadcrumb(name="Update tags"))
        return context


class TagByTag(TagReferences):
    """
    Tag references with a specific tag.
    """

    model = models.ReferenceFilterTag

    def get_assessment(self, request, *args, **kwargs):
        self.object = get_object_or_404(self.model, pk=self.kwargs.get("pk"))
        return self.object.get_assessment()

    def get_ref_qs_filters(self):
        return dict(tags=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][3] = Breadcrumb(name=f'Update "{self.object.name}" tags')
        return context


class TagByUntagged(TagReferences):
    """
    View to tag all untagged references for an assessment.
    """

    model = Assessment

    def get_assessment(self, request, *args, **kwargs):
        self.object = get_object_or_404(Assessment, id=self.kwargs.get("pk"))
        return self.object

    def get_ref_qs_filters(self):
        return dict(tags=self.object.pk)

    def get_context_data(self, **kwargs):
        self.qs_reference = self.assessment.references.all().untagged()
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][3] = Breadcrumb(name="Tag untagged references")
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
    filterset_class = dynamic_filterset(
        filterset.ReferenceFilterSet,
        grid_layout={
            "rows": [
                {"columns": [{"width": 3}, {"width": 3}, {"width": 3}, {"width": 3}]},
                {
                    "columns": [
                        {
                            "width": 5,
                            "rows": [
                                {
                                    "columns": [
                                        {"width": 12},
                                        {"width": 12},
                                        {"width": 6},
                                        {"width": 6},
                                    ]
                                }
                            ],
                        },
                        {"width": 7},
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


class RefUploadExcel(ProjectManagerOrHigherMixin, MessageMixin, FormView):
    """
    Upload Excel files and update reference details.
    """

    model = Assessment
    template_name = "lit/reference_upload_excel.html"
    form_class = forms.ReferenceExcelUploadForm

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.model, pk=kwargs["pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["assessment"] = self.assessment
        return kwargs

    def form_valid(self, form):
        errors = models.Reference.objects.process_excel(form.cleaned_data["df"], self.assessment.id)
        if len(errors) > 0:
            msg = """References updated, but some errors were found
                (references with errors were not updated): {0}""".format(
                listToUl(errors)
            )
        else:
            msg = "References updated."
        self.success_message = msg
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = lit_overview_crumbs(
            self.request.user, self.assessment, "Reference upload"
        )
        return context

    def get_success_url(self):
        return reverse_lazy("lit:overview", args=[self.assessment.pk])


class RefListExtract(TeamMemberOrHigherMixin, MessageMixin, FormView):
    template_name = "lit/reference_extract_list.html"
    breadcrumb_active_name = "Prepare for extraction"
    model = Assessment
    form_class = forms.BulkReferenceStudyExtractForm
    success_message = "Selected references were successfully converted to studies."

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.model, pk=kwargs["pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            assessment=self.assessment,
            reference_qs=models.Reference.objects.get_references_ready_for_import(self.assessment),
        )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            breadcrumbs=lit_overview_crumbs(self.request.user, self.assessment, "Convert to study"),
            object_list=context["form"].fields["references"].queryset,
        )
        return context

    def get_success_url(self):
        return reverse_lazy("lit:ref_list_extract", args=[self.assessment.pk])

    def form_valid(self, form):
        form.bulk_create_studies()
        return super().form_valid(form)


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

    def permission_check_user_can_edit(self):
        # perform standard check
        super().permission_check_user_can_edit()
        # and additional check
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


class RefTopicModel(BaseDetail):
    model = models.LiteratureAssessment
    template_name = "lit/topic_model.html"
    breadcrumb_active_name = "Topic model"

    def get_object(self, queryset=None):
        # use the assessment_id as the primary key instead of the models.LiteratureAssessment
        assessment_id = self.kwargs.get(self.pk_url_kwarg)
        object_ = get_object_or_404(self.model, assessment_id=assessment_id)
        return super().get_object(object=object_)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["num_references"] = self.object.assessment.references.count()
        context["breadcrumbs"][2] = lit_overview_breadcrumb(self.assessment)
        context["data"] = json.dumps(
            dict(
                topicModelUrl=self.object.get_topic_model_url(),
                topicModelRefreshUrl=self.object.get_topic_model_refresh_url(),
            )
        )
        return context


class TagsUpdate(WebappMixin, ProjectManagerOrHigherMixin, DetailView):
    """
    Update tags for an assessment. Note that right now, only project managers
    of the assessment can update tags. (we use the Assessment as the model in an
    update-view, which only project-managers have permission to do-so).
    """

    model = Assessment
    template_name = "lit/tags_update.html"

    def get_assessment(self, request, *args, **kwargs):
        return self.get_object()

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


class LiteratureAssessmentUpdate(ProjectManagerOrHigherMixin, BaseUpdate):
    success_message = "Literature assessment settings updated."
    model = models.LiteratureAssessment
    form_class = forms.LiteratureAssessmentForm

    def get_assessment(self, request, *args, **kwargs):
        return self.get_object().assessment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][2] = lit_overview_breadcrumb(self.assessment)
        return context

    def get_success_url(self):
        return reverse_lazy("lit:tags_update", args=(self.assessment.id,))


class TagsCopy(AssessmentPermissionsMixin, MessageMixin, FormView):
    """
    Remove exiting tags and copy all tags from a separate assessment.
    """

    model = Assessment
    template_name = "lit/tags_copy.html"
    form_class = forms.TagsCopyForm
    success_message = "Literature tags for this assessment have been updated"

    def dispatch(self, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=kwargs["pk"])
        self.permission_check_user_can_edit()
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assessment"] = self.assessment
        context["breadcrumbs"] = lit_overview_crumbs(
            self.request.user, self.assessment, "Copy tags"
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["assessment"] = self.assessment
        return kwargs

    def form_valid(self, form):
        form.copy_tags()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("lit:tags_update", kwargs={"pk": self.assessment.pk})


class BulkTagReferences(TeamMemberOrHigherMixin, BaseDetail):
    model = Assessment
    template_name = "lit/bulk_tag_references.html"

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.model, pk=kwargs["pk"])

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
