from django.http import HttpRequest
from django.shortcuts import render

from ..assessment.models import Assessment, TimeSpentEditing
from ..common.htmx import HtmxViewSet, action, can_edit, can_view
from ..common.views import (
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseFilterList,
    BaseUpdate,
    HeatmapBase,
)
from ..mgmt.views import EnsureExtractionStartedMixin
from ..study.models import Study
from . import filterset, forms, models


class HeatmapStudyDesign(HeatmapBase):
    heatmap_data_class = "epidemiology-v2-study-design"
    heatmap_data_url = "epiv2:api:assessment-study-export"
    heatmap_view_title = "Epidemiology study design"


class HeatmapResult(HeatmapBase):
    heatmap_data_class = "epidemiology-v2-result-summary"
    heatmap_data_url = "epiv2:api:assessment-export"
    heatmap_view_title = "Epidemiology data extraction"


class OutcomeView(BaseFilterList):
    parent_model = Assessment
    model = models.Outcome
    filterset_class = filterset.OutcomeFilterSet


# Design (Study Population)
class DesignCreate(EnsureExtractionStartedMixin, BaseCreate):
    success_message = "Study-population created."
    parent_model = Study
    parent_template_name = "study"
    model = models.Design
    form_class = forms.DesignForm

    def get_success_url(self):
        super().get_success_url()  # trigger EnsureExtractionStarted
        return self.object.get_update_url()


class DesignUpdate(BaseUpdate):
    success_message = "Study-population updated."
    parent_model = Study
    parent_template_name = "study"
    model = models.Design
    form_class = forms.DesignForm
    template_name = "epiv2/design_update.html"

    def get_queryset(self):
        return super().get_queryset().complete()


class DesignDetail(BaseDetail):
    model = models.Design

    def get_queryset(self):
        return super().get_queryset().complete()


class DesignDelete(BaseDelete):
    success_message = "Study Population deleted."
    model = models.Design

    def get_queryset(self):
        return super().get_queryset().complete()

    def get_success_url(self):
        return self.object.study.get_absolute_url()


# Design viewset
class DesignViewSet(HtmxViewSet):
    actions = {"read", "update"}
    parent_model = Study
    model = models.Design
    form_fragment = "epiv2/fragments/_design_edit.html"
    detail_fragment = "epiv2/fragments/_design_table.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = forms.DesignForm(data=data, instance=request.item.object)
        if request.method == "GET":
            TimeSpentEditing.set_start_time(request)
        elif request.method == "POST" and form.is_valid():
            TimeSpentEditing.add_time_spent_job(
                request, request.item.object, request.item.assessment.id
            )
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)


class DesignChildViewSet(HtmxViewSet):
    actions = {"create", "read", "update", "delete", "clone"}
    parent_model = models.Design
    model = None  # required
    form_class = None  # required
    form_fragment = "epiv2/fragments/_object_edit_row.html"
    detail_fragment = None  # required

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "GET":
            form = self.form_class(parent=request.item.parent)
            TimeSpentEditing.set_start_time(request)
        else:
            form = self.form_class(request.POST, parent=request.item.parent)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
                TimeSpentEditing.add_time_spent_job(
                    request, request.item.object, request.item.assessment.id
                )
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = self.form_class(data=data, instance=request.item.object)
        if request.method == "GET":
            TimeSpentEditing.set_start_time(request)
        elif request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
            TimeSpentEditing.add_time_spent_job(
                request, request.item.object, request.item.assessment.id
            )
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            context = {"attribute": self.model.__name__.lower(), "id": request.item.object.id}
            self.perform_delete(request.item)
            return render(request, "epiv2/fragments/_delete_rows.html", context)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model"] = self.model.__name__.lower()
        return context


# Chemical viewset
class ChemicalViewSet(DesignChildViewSet):
    model = models.Chemical
    form_class = forms.ChemicalForm
    detail_fragment = "epiv2/fragments/chemical_row.html"


# Exposure viewset
class ExposureViewSet(DesignChildViewSet):
    model = models.Exposure
    form_class = forms.ExposureForm
    detail_fragment = "epiv2/fragments/exposure_row.html"


# Chemical viewset
class ExposureLevelViewSet(DesignChildViewSet):
    model = models.ExposureLevel
    form_class = forms.ExposureLevelForm
    detail_fragment = "epiv2/fragments/exposurelevel_row.html"


# Outcome viewset
class OutcomeViewSet(DesignChildViewSet):
    model = models.Outcome
    form_class = forms.OutcomeForm
    detail_fragment = "epiv2/fragments/outcome_row.html"


# Adjustment factor viewset
class AdjustmentFactorViewSet(DesignChildViewSet):
    model = models.AdjustmentFactor
    form_class = forms.AdjustmentFactorForm
    detail_fragment = "epiv2/fragments/adjustment_factor_row.html"


# Data extraction viewset
class DataExtractionViewSet(DesignChildViewSet):
    model = models.DataExtraction
    form_class = forms.DataExtractionForm
    detail_fragment = "epiv2/fragments/data_extraction_row.html"
