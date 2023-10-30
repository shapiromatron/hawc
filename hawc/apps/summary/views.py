import itertools
import json
import re

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import RedirectView, TemplateView

from ..assessment.constants import AssessmentViewPermissions
from ..assessment.models import Assessment
from ..assessment.views import check_published_status
from ..common.crumbs import Breadcrumb
from ..common.helper import WebappConfig
from ..common.views import (
    BaseCopyForm,
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseFilterList,
    BaseList,
    BaseUpdate,
)
from ..riskofbias.models import RiskOfBiasMetric
from . import constants, filterset, forms, models, prefilters, serializers


def get_visual_list_crumb(assessment) -> Breadcrumb:
    return Breadcrumb(
        name="Visualizations", url=reverse("summary:visualization_list", args=(assessment.id,))
    )


def get_summary_list_crumb(assessment) -> Breadcrumb:
    return Breadcrumb(name="Summary", url=reverse("summary:list", args=(assessment.id,)))


def get_table_list_crumb(assessment) -> Breadcrumb:
    return Breadcrumb(
        name="Summary tables", url=reverse("summary:tables_list", args=(assessment.id,))
    )


# SUMMARY-TEXT
class SummaryTextList(BaseList):
    parent_model = Assessment
    model = models.SummaryText
    breadcrumb_active_name = "Executive summary"

    def get_queryset(self):
        rt = self.model.get_assessment_root_node(self.assessment.id)
        return super().get_queryset().filter(pk__in=[rt.pk])

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="summaryTextStartup", data=dict(assessment_id=self.assessment.id, editMode=False)
        )


class SummaryTextModify(BaseCreate):
    # Base view for all Create, Update, Delete GET operations
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.SummaryText
    form_class = forms.SummaryTextForm
    http_method_names = ("get",)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["smart_tag_form"] = forms.SmartTagForm(assessment_id=self.assessment.id)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(
            self.request.user,
            "Update text",
            [Breadcrumb.from_object(self.assessment), get_summary_list_crumb(self.assessment)],
        )
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="summaryTextStartup",
            data=dict(
                assessment_id=self.assessment.id,
                editMode=True,
                csrf=get_token(self.request),
            ),
        )


# SUMMARY TABLE
class GetSummaryTableMixin:
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        slug = self.kwargs.get("slug")
        assessment = self.kwargs.get("pk")
        obj = get_object_or_404(models.SummaryTable, assessment=assessment, slug=slug)
        obj = super().get_object(object=obj)
        check_published_status(self.request.user, obj.published, self.assessment)
        return obj


class SummaryTableList(BaseFilterList):
    parent_model = Assessment
    model = models.SummaryTable
    filterset_class = filterset.SummaryTableFilterSet
    breadcrumb_active_name = "Summary tables"

    def get_filterset_form_kwargs(self):
        if self.assessment.user_is_team_member_or_higher(self.request.user):
            return dict(
                main_field="title",
                appended_fields=["type", "published"],
            )
        else:
            return dict(
                main_field="title", appended_fields=["type"], dynamic_fields=["title", "type"]
            )


class SummaryTableDetail(GetSummaryTableMixin, BaseDetail):
    model = models.SummaryTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context["object"].published is False and context["obj_perms"]["edit"] is False:
            raise PermissionDenied()
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_table_list_crumb(self.assessment)
        )
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(app="summaryTableViewStartup", data=dict(table_id=self.object.id))


class SummaryTableCreateSelector(BaseCreate):
    success_message = None
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.SummaryTable
    form_class = forms.SummaryTableSelectorForm
    template_name = "summary/summarytable_selector.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_table_list_crumb(self.assessment)
        )
        return context

    def form_valid(self, form):
        url = reverse(
            "summary:tables_create",
            args=(
                form.assessment.id,
                form.cleaned_data["table_type"],
            ),
        )
        return HttpResponseRedirect(url)


class SummaryTableCreate(BaseCreate):
    success_message = "Summary table created."
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.SummaryTable
    form_class = forms.SummaryTableForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        try:
            table_type = constants.TableType(self.kwargs["table_type"])
        except ValueError:
            raise Http404()
        kwargs["table_type"] = table_type
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_table_list_crumb(self.assessment)
        )
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="summaryTableEditStartup",
            data=dict(
                assessment_id=self.assessment.id,
                is_create=True,
                initial=serializers.SummaryTableSerializer(context["form"].instance).data,
                save_url=models.SummaryTable.get_api_list_url(self.assessment.id),
                cancel_url=models.SummaryTable.get_list_url(self.assessment.id),
                csrf=get_token(self.request),
            ),
        )


class SummaryTableCopy(BaseCopyForm):
    copy_model = models.SummaryTable
    form_class = forms.SummaryTableCopySelectorForm
    model = Assessment

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw.update(parent=self.assessment, user=self.request.user)
        return kw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(
            self.request.user,
            "Copy existing",
            [Breadcrumb.from_object(self.assessment), get_table_list_crumb(self.assessment)],
        )
        return context


class SummaryTableUpdate(GetSummaryTableMixin, BaseUpdate):
    success_message = "Summary table updated."
    model = models.SummaryTable
    form_class = forms.SummaryTableForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 2, get_table_list_crumb(self.assessment)
        )
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="summaryTableEditStartup",
            data=dict(
                assessment_id=self.assessment.id,
                is_create=False,
                initial=serializers.SummaryTableSerializer(self.object).data,
                save_url=self.object.get_api_url(),
                cancel_url=self.object.get_absolute_url(),
                csrf=get_token(self.request),
            ),
        )


class SummaryTableDelete(GetSummaryTableMixin, BaseDelete):
    success_message = "Summary table deleted."
    model = models.SummaryTable

    def get_success_url(self):
        return self.model.get_list_url(self.assessment.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 2, get_table_list_crumb(self.assessment)
        )
        return context


# VISUALIZATIONS
class GetVisualizationObjectMixin:
    def get_object(self):
        slug = self.kwargs.get("slug")
        assessment = self.kwargs.get("pk")
        obj = get_object_or_404(models.Visual, assessment=assessment, slug=slug)
        obj = super().get_object(object=obj)
        check_published_status(self.request.user, obj.published, self.assessment)
        return obj


class VisualizationList(BaseFilterList):
    parent_model = Assessment
    model = models.Visual
    breadcrumb_active_name = "Visualizations"
    filterset_class = filterset.VisualFilterSet

    @property
    def visual_fs(self):
        if not hasattr(self, "_visual_fs"):
            data = self.request.GET.copy()
            # only include type if it is a visual type
            if "type" in data:
                match = re.search(r"v-(\d+)$", data["type"])
                if match:
                    data["type"] = match.group(1)
            self._visual_fs = filterset.VisualFilterSet(
                data=data, request=self.request, assessment=self.assessment
            )
        return self._visual_fs

    @property
    def data_pivot_fs(self):
        if not hasattr(self, "_data_pivot_fs"):
            data = self.request.GET.copy()
            # only include type if it is a data pivot type
            if "type" in data:
                match = re.search(r"dp-(\d+)$", data["type"])
                if match:
                    data["type"] = match.group(1)
            self._data_pivot_fs = filterset.DataPivotFilterSet(
                data=data, request=self.request, assessment=self.assessment
            )
        return self._data_pivot_fs

    @property
    def form(self):
        if not hasattr(self, "_form"):
            fs = filterset.VisualFilterSet(
                data=self.request.GET,
                request=self.request,
                assessment=self.assessment,
                form_kwargs=self.get_filterset_form_kwargs(),
            )
            form = fs.form
            # combine type choices for both visual and data pivot
            form.fields["type"].choices = [
                (f"v-{choice}", _)
                for choice, _ in self.visual_fs.form.fields["type"].choices
                if choice != ""
            ] + [
                (f"dp-{choice}", _)
                for choice, _ in self.data_pivot_fs.form.fields["type"].choices
                if choice != ""
            ]
            self._form = form
        return self._form

    def get_item_list(self):
        self.form.is_valid()
        # prefilter by type, ie if it is a visual type or data pivot type
        choice = self.form.cleaned_data.get("type", "")
        if choice != "":
            if choice.startswith("v-"):
                items = self.visual_fs.qs
            else:
                items = self.data_pivot_fs.qs
        else:
            items = list(itertools.chain(self.visual_fs.qs, self.data_pivot_fs.qs))
        return sorted(items, key=lambda d: d.title.lower())

    def get_filterset_form_kwargs(self):
        if self.assessment.user_is_team_member_or_higher(self.request.user):
            return dict(
                main_field="title",
                appended_fields=["type", "published"],
            )
        else:
            return dict(
                main_field="title", appended_fields=["type"], dynamic_fields=["title", "type"]
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["objects"] = self.get_item_list()
        context["n_objects"] = len(context["objects"])
        context["form"] = self.form
        return context


class VisualizationByIdDetail(RedirectView):
    """
    Redirect to standard visual page; useful for developers referencing by database id.
    """

    def get_redirect_url(*args, **kwargs):
        return get_object_or_404(models.Visual, id=kwargs.get("pk")).get_absolute_url()


class VisualizationDetail(GetVisualizationObjectMixin, BaseDetail):
    model = models.Visual

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_visual_list_crumb(self.assessment)
        )
        return context

    def get_template_names(self):
        if self.object.visual_type == constants.VisualType.PLOTLY:
            return "summary/visual_detail_plotly.html"
        else:
            return super().get_template_names()


class VisualizationCreateSelector(BaseDetail):
    model = Assessment
    template_name = "summary/visual_selector.html"
    breadcrumb_active_name = "Visualization selector"

    def get_context_data(self, **kwargs):
        kwargs.update(
            action="Create",
            viz_url_pattern="summary:visualization_create",
            dp_url_pattern="summary:dp_new-prompt",
        )
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_visual_list_crumb(self.assessment)
        )
        return context


class VisualizationCreate(BaseCreate):
    success_message = "Visualization created."
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.Visual

    def get_form_class(self):
        visual_type = int(self.kwargs.get("visual_type"))
        return forms.get_visual_form(visual_type)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["visual_type"] = self.kwargs.get("visual_type")
        try:
            constants.VisualType(kwargs["visual_type"])
        except ValueError:
            raise Http404

        if kwargs["initial"]:
            kwargs["instance"] = self.model.objects.filter(pk=self.request.GET["initial"]).first()
            kwargs["instance"].pk = None
            self.instance = kwargs["instance"]
            kwargs["evidence_type"] = kwargs["instance"].evidence_type

        else:
            kwargs["evidence_type"] = self.kwargs.get("study_type")
            if kwargs["evidence_type"] is None:
                try:
                    kwargs["evidence_type"] = constants.get_default_evidence_type(
                        kwargs["visual_type"]
                    )
                except ValueError:
                    raise Http404
            if (
                kwargs["evidence_type"]
                not in constants.VISUAL_EVIDENCE_CHOICES[kwargs["visual_type"]]
            ):
                raise Http404
        self.evidence_type = kwargs["evidence_type"]
        return kwargs

    def get_template_names(self):
        visual_type = int(self.kwargs.get("visual_type"))
        if visual_type in {
            constants.VisualType.BIOASSAY_AGGREGATION,
            constants.VisualType.LITERATURE_TAGTREE,
            constants.VisualType.EXTERNAL_SITE,
            constants.VisualType.PLOTLY,
        }:
            if (
                visual_type == constants.VisualType.PLOTLY
                and not settings.HAWC_FEATURES.ENABLE_PLOTLY_VISUAL
            ):
                raise PermissionDenied()
            return "summary/visual_form_django.html"
        else:
            return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dose_units"] = models.Visual.get_dose_units()
        context["instance"] = {}
        context["visual_type"] = int(self.kwargs.get("visual_type"))
        context["evidence_type"] = self.evidence_type
        context["smart_tag_form"] = forms.SmartTagForm(assessment_id=self.assessment.id)
        context["rob_metrics"] = json.dumps(
            list(RiskOfBiasMetric.objects.get_metrics_for_visuals(self.assessment.id))
        )
        context["initial_data"] = json.dumps(self.get_initial_visual(context))
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_visual_list_crumb(self.assessment)
        )
        return context

    def get_initial_visual(self, context) -> dict:
        instance = context["form"].instance
        instance.id = instance.FAKE_INITIAL_ID
        return serializers.VisualSerializer().to_representation(instance)


class VisualizationCreateTester(VisualizationCreate):
    parent_model = Assessment
    http_method_names = ("post",)

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        response = form.instance.get_editing_dataset(request)
        return JsonResponse(response)


class VisualizationCopySelector(BaseDetail):
    model = Assessment
    template_name = "summary/visual_selector.html"
    breadcrumb_active_name = "Visualization selector"
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER

    def get_context_data(self, **kwargs):
        kwargs.update(
            action="Copy",
            viz_url_pattern="summary:visualization_copy",
            dp_url_pattern="summary:dp_copy_selector",
        )
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_visual_list_crumb(self.assessment)
        )
        return context


class VisualizationCopy(BaseCopyForm):
    copy_model = models.Visual
    form_class = forms.VisualSelectorForm
    model = Assessment

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["queryset"] = models.Visual.objects.clonable_queryset(self.request.user).filter(
            visual_type=self.kwargs["visual_type"]
        )
        return kw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(
            self.request.user,
            "Copy existing",
            [Breadcrumb.from_object(self.assessment), get_visual_list_crumb(self.assessment)],
        )
        return context


class VisualizationUpdate(GetVisualizationObjectMixin, BaseUpdate):
    success_message = "Visualization updated."
    model = models.Visual

    def get_form_class(self):
        try:
            return forms.get_visual_form(self.object.visual_type)
        except ValueError:
            raise Http404

    def get_template_names(self):
        visual_type = self.object.visual_type
        if visual_type in {
            constants.VisualType.BIOASSAY_AGGREGATION,
            constants.VisualType.LITERATURE_TAGTREE,
            constants.VisualType.EXTERNAL_SITE,
            constants.VisualType.PLOTLY,
        }:
            if (
                visual_type == constants.VisualType.PLOTLY
                and not settings.HAWC_FEATURES.ENABLE_PLOTLY_VISUAL
            ):
                raise PermissionDenied()
            return "summary/visual_form_django.html"
        else:
            return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dose_units"] = models.Visual.get_dose_units()
        context["instance"] = self.object.get_json()
        context["visual_type"] = self.object.visual_type
        context["evidence_type"] = self.object.evidence_type
        context["smart_tag_form"] = forms.SmartTagForm(assessment_id=self.assessment.id)
        context["rob_metrics"] = json.dumps(
            list(RiskOfBiasMetric.objects.get_metrics_for_visuals(self.assessment.id))
        )
        context["initial_data"] = json.dumps(
            serializers.VisualSerializer().to_representation(self.object)
        )
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 2, get_visual_list_crumb(self.assessment)
        )
        return context


class VisualizationDelete(GetVisualizationObjectMixin, BaseDelete):
    success_message = "Visualization deleted."
    model = models.Visual

    def get_success_url(self):
        return reverse_lazy("summary:visualization_list", kwargs={"pk": self.assessment.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 2, get_visual_list_crumb(self.assessment)
        )
        return context


# DATA-PIVOT
class DataPivotNewPrompt(BaseDetail):
    """
    Select if you wish to upload a file or use a query.
    """

    model = Assessment
    template_name = "summary/datapivot_type_selector.html"
    breadcrumb_active_name = "Data Pivot selector"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["evidence_type"] = constants.StudyType
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_visual_list_crumb(self.assessment)
        )
        return context


class DataPivotNew(BaseCreate):
    # abstract view; extended below for actual use
    parent_model = Assessment
    parent_template_name = "assessment"
    success_message = "Data Pivot created."
    template_name = "summary/datapivot_form.html"

    def get_success_url(self):
        super().get_success_url()
        return self.object.get_visualization_update_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        reset_rows = self.request.GET.get("reset_row_overrides")
        settings = kwargs["initial"].get("settings")
        if reset_rows and settings:
            models.DataPivot.reset_row_overrides(settings)
        return kwargs


class DataPivotQueryNew(DataPivotNew):
    model = models.DataPivotQuery
    form_class = forms.DataPivotQueryForm
    template_name = "summary/datapivot_form.html"

    def get_evidence_type(self) -> constants.StudyType:
        try:
            evidence_type = constants.StudyType(self.kwargs["study_type"])
            _ = prefilters.get_prefilter_cls(None, evidence_type, self.assessment)
        except (KeyError, ValueError):
            raise Http404
        return evidence_type

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["evidence_type"] = self.get_evidence_type()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["file_loader"] = False
        context["smart_tag_form"] = forms.SmartTagForm(assessment_id=self.assessment.id)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_visual_list_crumb(self.assessment)
        )
        return context


class DataPivotFileNew(DataPivotNew):
    model = models.DataPivotUpload
    form_class = forms.DataPivotUploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["file_loader"] = True
        context["smart_tag_form"] = forms.SmartTagForm(assessment_id=self.assessment.id)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_visual_list_crumb(self.assessment)
        )
        return context


class DataPivotCopyAsNewSelector(BaseCopyForm):
    copy_model = models.DataPivot
    form_class = forms.DataPivotSelectorForm
    model = Assessment

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw.update(user=self.request.user)
        return kw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(
            self.request.user,
            "Copy existing",
            [Breadcrumb.from_object(self.assessment), get_visual_list_crumb(self.assessment)],
        )
        return context


class GetDataPivotObjectMixin:
    def get_object(self):
        slug = self.kwargs.get("slug")
        assessment = self.kwargs.get("pk")
        obj = get_object_or_404(models.DataPivot, assessment=assessment, slug=slug)
        obj = obj.datapivotquery if hasattr(obj, "datapivotquery") else obj.datapivotupload
        obj = super().get_object(object=obj)
        check_published_status(self.request.user, obj.published, self.assessment)
        return obj


class DataPivotByIdDetail(RedirectView):
    """
    Redirect to standard data pivot page; useful for developers referencing by database id.
    """

    def get_redirect_url(*args, **kwargs):
        return get_object_or_404(models.DataPivot, id=kwargs.get("pk")).get_absolute_url()


class DataPivotDetail(GetDataPivotObjectMixin, BaseDetail):
    model = models.DataPivot
    template_name = "summary/datapivot_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_visual_list_crumb(self.assessment)
        )
        return context


class DataPivotUpdateSettings(GetDataPivotObjectMixin, BaseUpdate):
    success_message = "Data Pivot updated."
    model = models.DataPivot
    form_class = forms.DataPivotSettingsForm
    template_name = "summary/datapivot_update_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 2, get_visual_list_crumb(self.assessment)
        )
        context["config"] = {
            "data_url": self.object.get_data_url(),
            "settings": self.object.settings,
        }
        return context


class DataPivotUpdateQuery(GetDataPivotObjectMixin, BaseUpdate):
    success_message = "Data Pivot updated."
    model = models.DataPivotQuery
    form_class = forms.DataPivotQueryForm
    template_name = "summary/datapivot_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["file_loader"] = False
        context["smart_tag_form"] = forms.SmartTagForm(assessment_id=self.assessment.id)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 2, get_visual_list_crumb(self.assessment)
        )
        return context


class DataPivotUpdateFile(GetDataPivotObjectMixin, BaseUpdate):
    success_message = "Data Pivot updated."
    model = models.DataPivotUpload
    form_class = forms.DataPivotUploadForm
    template_name = "summary/datapivot_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["file_loader"] = True
        context["smart_tag_form"] = forms.SmartTagForm(assessment_id=self.assessment.id)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 2, get_visual_list_crumb(self.assessment)
        )
        return context


class DataPivotDelete(GetDataPivotObjectMixin, BaseDelete):
    success_message = "Data Pivot deleted."
    model = models.DataPivot
    template_name = "summary/datapivot_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("summary:visualization_list", kwargs={"pk": self.assessment.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 2, get_visual_list_crumb(self.assessment)
        )
        return context


class DatasetInteractivity(TemplateView):
    template_name = "summary/dataset_interactivity.html"
