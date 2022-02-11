from django.db.models import Prefetch
from django.http import HttpRequest
from django.shortcuts import render

from ..common.htmx import HtmxViewSet, action, can_edit, can_view
from ..common.views import BaseCreate, BaseDelete, BaseDetail, BaseUpdate
from ..study.models import Study
from . import forms, models


# Design (Study Population)
class DesignCreate(BaseCreate):
    success_message = "Study-population created."
    parent_model = Study
    parent_template_name = "study"
    model = models.Design
    form_class = forms.DesignForm


class DesignUpdate(BaseUpdate):
    success_message = "Study-population updated."
    parent_model = Study
    parent_template_name = "study"
    model = models.Design
    form_class = forms.DesignForm
    template_name = "epiv2/design_update.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "exposures",
                "outcomes",
                "chemicals",
                "criteria",
                "adjustment_factors",
                Prefetch(
                    "exposure_levels",
                    queryset=models.ExposureLevel.objects.select_related(
                        "chemical", "exposure_measurement"
                    ),
                ),
                Prefetch(
                    "data_extractions",
                    queryset=models.DataExtraction.objects.select_related(
                        "adjustment_factor", "outcome", "exposure_level"
                    ),
                ),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exposures"] = self.object.exposures.all()
        context["outcomes"] = self.object.outcomes.all()
        context["chemical"] = self.object.chemicals.all()
        context["criteria"] = self.object.criteria.all()
        context["exposure_levels"] = self.object.exposure_levels.all()
        context["adjustment_factors"] = self.object.adjustment_factors.all()
        context["data_extractions"] = self.object.data_extractions.all()
        return context


class DesignDetail(BaseDetail):
    model = models.Design

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "exposures",
                "outcomes",
                "chemicals",
                "criteria",
                "adjustment_factors",
                Prefetch(
                    "exposure_levels",
                    queryset=models.ExposureLevel.objects.select_related(
                        "chemical", "exposure_measurement"
                    ),
                ),
                Prefetch(
                    "data_extractions",
                    queryset=models.DataExtraction.objects.select_related(
                        "adjustment_factor", "outcome", "exposure_level"
                    ),
                ),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exposures"] = self.object.exposures.all()
        context["outcomes"] = self.object.outcomes.all()
        context["chemical"] = self.object.chemicals.all()
        context["criteria"] = self.object.criteria.all()
        context["exposure_levels"] = self.object.exposure_levels.all()
        context["adjustment_factors"] = self.object.adjustment_factors.all()
        context["data_extractions"] = self.object.data_extractions.all()
        return context


class DesignDelete(BaseDelete):
    success_message = "Study Population deleted."
    model = models.Design

    def get_success_url(self):
        return self.object.study.get_absolute_url()


# Design viewset
class DesignViewset(HtmxViewSet):
    actions = {"create", "read", "update", "delete", "clone"}
    parent_model = Study
    model = models.Design
    form_fragment = "epiv2/fragments/design_form_copy.html"
    detail_fragment = "epiv2/fragments/design_detail_frag.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = forms.DesignForm(data=data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)


# Criteria viewset
class CriteriaViewset(HtmxViewSet):
    actions = {"create", "read", "update", "delete", "clone"}
    parent_model = models.Design
    model = models.Criteria
    form_fragment = "epiv2/fragments/criteria_edit_row.html"
    detail_fragment = "epiv2/fragments/criteria_row.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = forms.CriteriaForm(request.POST, parent=request.item.parent)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
        else:
            form = forms.CriteriaForm()
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = forms.CriteriaForm(data=data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            context = {"attribute": "criteria", "id": request.item.object.id}
            self.perform_delete(request.item)
            return render(request, "epiv2/fragments/_delete_rows.html", context)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())


# Chemical viewset
class ChemicalViewset(HtmxViewSet):
    actions = {"create", "read", "update", "delete", "clone"}
    parent_model = models.Design
    model = models.Chemical
    form_fragment = "epiv2/fragments/chemical_edit_row.html"
    detail_fragment = "epiv2/fragments/chemical_row.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = forms.ChemicalForm(request.POST, parent=request.item.parent)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
        else:
            form = forms.ChemicalForm()
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = forms.ChemicalForm(data=data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            context = {"attribute": "chemical", "id": request.item.object.id}
            self.perform_delete(request.item)
            return render(request, "epiv2/fragments/_delete_rows.html", context)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())


# Exposure viewset
class ExposureViewset(HtmxViewSet):
    actions = {"create", "read", "update", "delete", "clone"}
    parent_model = models.Design
    model = models.Exposure
    form_fragment = "epiv2/fragments/exposure_edit_row.html"
    detail_fragment = "epiv2/fragments/exposure_row.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = forms.ExposureForm(request.POST, parent=request.item.parent)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
        else:
            form = forms.ExposureForm()
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = forms.ExposureForm(data=data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            context = {"attribute": "exposure", "id": request.item.object.id}
            self.perform_delete(request.item)
            return render(request, "epiv2/fragments/_delete_rows.html", context)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())


# Chemical viewset
class ExposureLevelViewset(HtmxViewSet):
    actions = {"create", "read", "update", "delete", "clone"}
    parent_model = models.Design
    model = models.ExposureLevel
    form_fragment = "epiv2/fragments/exposurelevel_edit_row.html"
    detail_fragment = "epiv2/fragments/exposurelevel_row.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = forms.ExposureLevelForm(request.POST, parent=request.item.parent)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
        else:
            form = forms.ExposureLevelForm()
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = forms.ExposureLevelForm(data=data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            context = {"attribute": "exposure_level", "id": request.item.object.id}
            self.perform_delete(request.item)
            return render(request, "epiv2/fragments/_delete_rows.html", context)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())


# Outcome viewset
class OutcomeViewset(HtmxViewSet):
    actions = {"create", "read", "update", "delete", "clone"}
    parent_model = models.Design
    model = models.Outcome
    form_fragment = "epiv2/fragments/outcome_edit_row.html"
    detail_fragment = "epiv2/fragments/outcome_row.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = forms.OutcomeForm(request.POST, parent=request.item.parent)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
        else:
            form = forms.OutcomeForm()
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = forms.OutcomeForm(data=data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            context = {"attribute": "outcome", "id": request.item.object.id}
            self.perform_delete(request.item)
            return render(request, "epiv2/fragments/_delete_rows.html", context)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())


# Adjustment factor viewset
class AdjustmentFactorViewset(HtmxViewSet):
    actions = {"create", "read", "update", "delete", "clone"}
    parent_model = models.Design
    model = models.AdjustmentFactor
    form_fragment = "epiv2/fragments/adjustment_factor_edit_row.html"
    detail_fragment = "epiv2/fragments/adjustment_factor_row.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = forms.AdjustmentFactorForm(request.POST, parent=request.item.parent)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
        else:
            form = forms.AdjustmentFactorForm()
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = forms.AdjustmentFactorForm(data=data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            context = {"attribute": "adjustment_factor", "id": request.item.object.id}
            self.perform_delete(request.item)
            return render(request, "epiv2/fragments/_delete_rows.html", context)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())


# Data extraction viewset
class DataExtractionViewset(HtmxViewSet):
    actions = {"create", "read", "update", "delete", "clone"}
    parent_model = models.Design
    model = models.DataExtraction
    form_fragment = "epiv2/fragments/data_extraction_edit_row.html"
    detail_fragment = "epiv2/fragments/data_extraction_row.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = forms.DataExtractionForm(request.POST, parent=request.item.parent)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
        else:
            form = forms.DataExtractionForm()
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = forms.DataExtractionForm(data=data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            context = {"attribute": "data_extraction", "id": request.item.object.id}
            self.perform_delete(request.item)
            return render(request, "epiv2/fragments/_delete_rows.html", context)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())
