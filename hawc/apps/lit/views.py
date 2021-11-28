import json
from typing import Dict, List

from django.core.exceptions import PermissionDenied
from django.forms.models import model_to_dict
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormView

from ..assessment.models import Assessment
from ..common.crumbs import Breadcrumb
from ..common.helper import WebappConfig, listToUl, tryParseInt
from ..common.views import (
    AssessmentPermissionsMixin,
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseList,
    BaseUpdate,
    MessageMixin,
    ProjectManagerOrHigherMixin,
    TeamMemberOrHigherMixin,
)
from . import constants, forms, models


def lit_overview_breadcrumb(assessment) -> Breadcrumb:
    return Breadcrumb(name="Literature review", url=reverse("lit:overview", args=(assessment.id,)))


def lit_overview_crumbs(user, assessment: Assessment, name: str) -> List[Breadcrumb]:
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
        context["config"] = json.dumps(
            {
                "tags": models.ReferenceFilterTag.get_all_tags(
                    self.assessment.id, json_encode=False
                ),
                "assessment_id": self.assessment.id,
                "referenceYearHistogramUrl": reverse(
                    "lit:api:assessment-reference-year-histogram", args=(self.assessment.id,)
                ),
            }
        )
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
        if self.object.search_type == "s":
            return forms.SearchForm
        elif self.object.search_type == "i":
            if self.object.source == constants.RIS:
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
        return context


class SearchQuery(BaseUpdate):
    model = models.Search
    form_class = forms.SearchForm
    http_method_names = ("get",)  # don't allow POST

    def get_object(self, **kwargs):
        obj = get_object_or_404(
            self.model, slug=self.kwargs.get(self.slug_url_kwarg), assessment=self.kwargs.get("pk"),
        )
        return super().get_object(object=obj)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.run_new_query()
        except models.TooManyPubMedResults as e:
            return HttpResponse(
                """
                                <p>PubMed Search error: <br>{0}</p>
                                <p>Please perform a more targeted-search.</p>
                                """.format(
                    e
                )
            )
        return HttpResponseRedirect(self.object.get_absolute_url())


class TagReferences(TeamMemberOrHigherMixin, FormView):
    """
    Abstract base-class to tag references, using various methods to get instance.
    """

    model = Assessment
    form_class = forms.TagReferenceForm
    template_name = "lit/reference_tag.html"

    def post(self, request, *args, **kwargs):
        if not self.request.is_ajax():
            raise Http404
        response = self.update_reference_tags()
        return HttpResponse(json.dumps(response), content_type="application/json")

    def update_reference_tags(self):
        # find reference, check that the assessment is the same as the one we
        # have permissions-checked for, and if so, update reference-tags
        response = {"status": "fail"}
        pk = tryParseInt(self.request.POST.get("pk"), -1)
        ref = models.Reference.objects.filter(pk=pk, assessment=self.assessment).first()
        if ref:
            tag_pks = self.request.POST.getlist("tags[]", [])
            ref.tags.set(tag_pks)
            ref.last_updated = timezone.now()
            ref.save()
            response["status"] = "success"
        return response

    def get_ref_qs_filters(self) -> Dict:
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
                tags=models.ReferenceFilterTag.get_all_tags(self.assessment.id, json_encode=False),
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
        self.qs_reference = models.Reference.objects.get_untagged_references(self.assessment)
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][3] = Breadcrumb(name="Tag untagged references")
        return context


def _get_reference_list(assessment, permissions, search=None) -> WebappConfig:
    return WebappConfig(
        app="litStartup",
        page="startupReferenceList",
        data=dict(
            assessment_id=assessment.id,
            search_id=search.id if search else None,
            tags=models.ReferenceFilterTag.get_all_tags(assessment.id, json_encode=False),
            references=models.Reference.objects.get_full_assessment_json(
                assessment, json_encode=False
            ),
            canEdit=permissions["edit"],
            untaggedReferenceCount=models.Reference.objects.get_untagged_references(
                assessment
            ).count(),
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
        context["config"] = _get_reference_list(
            self.assessment, context["obj_perms"], self.object
        ).dict()
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        context["breadcrumbs"].append(Breadcrumb(name="References"))
        return context


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
        context["object_type"] = "search"
        context["ref_objs"] = self.object.get_all_reference_tags()
        context["tags"] = models.ReferenceFilterTag.get_all_tags(self.assessment.id)
        context["objectType"] = self.model.__name__
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        context["breadcrumbs"].append(Breadcrumb(name="Visualization"))
        return context


class RefList(BaseList):
    parent_model = Assessment
    model = models.Reference

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["config"] = _get_reference_list(self.assessment, context["obj_perms"]).dict()
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        return context


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


class RefListExtract(BaseList):
    parent_model = Assessment
    model = models.Reference
    crud = "Update"  # update-level permission required despite list-view
    template_name = "lit/reference_extract_list.html"
    breadcrumb_active_name = "Prepare for extraction"

    def get_queryset(self):
        return self.model.objects.get_references_ready_for_import(self.assessment)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        return context


class RefDetail(BaseDetail):
    model = models.Reference

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = models.ReferenceFilterTag.get_all_tags(self.assessment.id)
        context["object_json"] = self.object.to_json()
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
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

    def permission_check_user_can_edit(self):
        # perform standard check
        super().permission_check_user_can_edit()
        # and additional check
        if self.object.has_study:
            raise PermissionDenied("Cannot delete - object has related study")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = models.ReferenceFilterTag.get_all_tags(self.assessment.id)
        context["object_json"] = self.object.to_json()
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        return context


class RefSearch(BaseDetail):
    model = Assessment
    template_name = "lit/reference_search.html"
    breadcrumb_active_name = "Reference search"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="litStartup",
            page="startupSearchReference",
            data=dict(
                assessment_id=self.assessment.id,
                canEdit=context["obj_perms"]["edit"],
                tags=models.ReferenceFilterTag.get_all_tags(self.assessment.id, json_encode=False),
                csrf=get_token(self.request),
            ),
        )


class RefsByTagJSON(BaseDetail):
    model = Assessment

    def get_context_data(self, **kwargs):
        response = {"status": "success", "refs": []}
        search_id = self.request.GET.get("search_id", None)
        if search_id is not None:
            search_id = int(search_id)

        tag_id = self.kwargs.get("tag_id", None)
        tag = None
        if tag_id != "untagged":
            tag = models.ReferenceFilterTag.get_tags_in_assessment(
                self.assessment.id, [int(tag_id)]
            )[0]

        if search_id:
            search = models.Search.objects.get(id=search_id)
            qs = search.get_references_with_tag(tag=tag, descendants=True)
        elif tag:
            qs = models.Reference.objects.get_references_with_tag(tag, descendants=True)
        else:
            qs = models.Reference.objects.get_untagged_references(self.assessment)

        response["refs"] = [
            ref.to_dict()
            for ref in qs.select_related("study").prefetch_related("searches", "identifiers")
        ]
        self.response = response

    def render_to_response(self, context, **response_kwargs):
        return HttpResponse(json.dumps(self.response), content_type="application/json")


class RefVisualization(BaseDetail):
    model = Assessment
    template_name = "lit/reference_visual.html"
    breadcrumb_active_name = "Visualization"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_type"] = "reference"
        context["ref_objs"] = models.Reference.objects.get_full_assessment_json(self.assessment)
        context["tags"] = models.ReferenceFilterTag.get_all_tags(self.assessment.id)
        context["objectType"] = self.model.__name__
        context["breadcrumbs"].insert(2, lit_overview_breadcrumb(self.assessment))
        return context


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


class TagsJSON(BaseDetail):
    model = Assessment

    def get_object(self, **kwargs):
        pk = tryParseInt(self.request.GET.get("pk"), -1)
        obj = get_object_or_404(self.model, pk=pk)
        return super().get_object(object=obj)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        tags = models.ReferenceFilterTag.get_all_tags(self.object.id)
        return HttpResponse(json.dumps(tags), content_type="application/json")


class TagsUpdate(ProjectManagerOrHigherMixin, DetailView):
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
        context["config"] = {
            "assessment_id": self.assessment.id,
            "csrf": get_token(self.request),
        }
        context["breadcrumbs"] = lit_overview_crumbs(
            self.request.user, self.assessment, "Bulk tag references"
        )
        return context
