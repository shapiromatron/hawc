import itertools
import json
import re

from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, RedirectView, TemplateView

from ..assessment.models import Assessment
from ..common.crumbs import Breadcrumb
from ..common.filterset import dynamic_filterset
from ..common.helper import WebappConfig
from ..common.views import (
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseFilterList,
    BaseList,
    BaseUpdate,
    TeamMemberOrHigherMixin,
)
from ..riskofbias.models import RiskOfBiasMetric
from . import constants, filterset, forms, models, serializers


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
        return self.model.objects.filter(pk__in=[rt.pk])

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
        return super().get_object(object=obj)


class SummaryTableList(BaseFilterList):
    parent_model = Assessment
    model = models.SummaryTable
    filterset_class = dynamic_filterset(
        filterset.SummaryTableFilterSet,
        grid_layout={"rows": [{"columns": [{"width": 6}, {"width": 3}, {"width": 3}]}]},
    )
    breadcrumb_active_name = "Summary tables"


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
        kwargs["table_type"] = self.kwargs["table_type"]
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


class SummaryTableCopy(TeamMemberOrHigherMixin, FormView):
    template_name = "summary/copy_selector.html"
    model = Assessment
    form_class = forms.SummaryTableCopySelectorForm

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(Assessment, pk=self.kwargs["pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            cancel_url=reverse("summary:visualization_list", args=(self.assessment.id,)),
            assessment_id=self.assessment.id,
            queryset=models.SummaryTable.objects.clonable_queryset(self.request.user).filter(
                assessment=self.assessment
            ),
        )
        return kwargs

    def form_valid(self, form):
        return HttpResponseRedirect(form.get_create_url())

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
        return super().get_object(object=obj)


class VisualizationList(BaseList):
    parent_model = Assessment
    model = models.Visual
    breadcrumb_active_name = "Visualizations"

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
            CombinedForm = dynamic_filterset(
                filterset.VisualFilterSet,
                grid_layout={"rows": [{"columns": [{"width": 6}, {"width": 3}, {"width": 3}]}]},
            )
            form = CombinedForm(
                data=self.request.GET, request=self.request, assessment=self.assessment
            ).form
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
        try:
            return forms.get_visual_form(visual_type)
        except ValueError:
            raise Http404

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["visual_type"] = int(self.kwargs.get("visual_type"))
        if kwargs["initial"]:
            kwargs["instance"] = self.model.objects.filter(pk=self.request.GET["initial"]).first()
            kwargs["instance"].pk = None
            self.instance = kwargs["instance"]
        return kwargs

    def get_template_names(self):
        visual_type = int(self.kwargs.get("visual_type"))
        if visual_type in {
            constants.VisualType.LITERATURE_TAGTREE,
            constants.VisualType.EXTERNAL_SITE,
        }:
            return "summary/visual_form_django.html"
        else:
            return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dose_units"] = models.Visual.get_dose_units()
        context["instance"] = {}
        context["visual_type"] = int(self.kwargs.get("visual_type"))
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
        if context["form"].initial:
            instance = self.instance
            instance.id = instance.FAKE_INITIAL_ID
        else:
            instance = self.model()
            instance.id = instance.FAKE_INITIAL_ID
            instance.assessment = self.assessment
            instance.visual_type = context["visual_type"]
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


class VisualizationCopy(TeamMemberOrHigherMixin, FormView):
    template_name = "summary/copy_selector.html"
    model = Assessment
    form_class = forms.VisualSelectorForm

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(Assessment, pk=self.kwargs["pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            assessment_id=self.assessment.id,
            cancel_url=reverse("summary:visualization_list", args=(self.assessment.id,)),
            queryset=models.Visual.objects.clonable_queryset(self.request.user).filter(
                visual_type=self.kwargs["visual_type"], assessment__pk=self.assessment.id
            ),
        )
        return kwargs

    def form_valid(self, form):
        return HttpResponseRedirect(form.get_create_url())

    def get_context_data(self, **kwargs):
        kwargs["breadcrumbs"] = Breadcrumb.build_crumbs(
            self.request.user,
            "Copy existing",
            [Breadcrumb.from_object(self.assessment), get_visual_list_crumb(self.assessment)],
        )
        return super().get_context_data(**kwargs)


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
            constants.VisualType.LITERATURE_TAGTREE,
            constants.VisualType.EXTERNAL_SITE,
        }:
            return "summary/visual_form_django.html"
        else:
            return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dose_units"] = models.Visual.get_dose_units()
        context["instance"] = self.object.get_json()
        context["visual_type"] = self.object.visual_type
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
        if self.request.GET.get("reset_row_overrides"):
            kwargs["initial"]["settings"] = models.DataPivot.reset_row_overrides(
                kwargs["initial"]["settings"]
            )
        return kwargs


class DataPivotQueryNew(DataPivotNew):
    model = models.DataPivotQuery
    form_class = forms.DataPivotQueryForm

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


class DataPivotCopyAsNewSelector(TeamMemberOrHigherMixin, FormView):
    # Select an existing assessed outcome as a template for a new one
    model = Assessment
    template_name = "summary/copy_selector.html"
    form_class = forms.DataPivotSelectorForm

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(Assessment, pk=self.kwargs.get("pk"))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["cancel_url"] = reverse("summary:visualization_list", args=(self.assessment.id,))
        return kwargs

    def form_valid(self, form):
        dp = form.cleaned_data["dp"]

        if hasattr(dp, "datapivotupload"):
            url = reverse_lazy("summary:dp_new-file", kwargs={"pk": self.assessment.id})
        else:
            url = reverse_lazy("summary:dp_new-query", kwargs={"pk": self.assessment.id})

        url += f"?initial={dp.pk}"

        if form.cleaned_data["reset_row_overrides"]:
            url += "&reset_row_overrides=1"

        return HttpResponseRedirect(url)

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
        if hasattr(obj, "datapivotquery"):
            obj = obj.datapivotquery
        else:
            obj = obj.datapivotupload
        return super().get_object(object=obj)


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
