from django.http import HttpRequest
from django.shortcuts import render

from ..common.htmx import HtmxViewSet, action, can_edit, can_view, is_htmx
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exposures"] = models.Exposure.objects.filter(design__id=self.object.pk)
        context["outcomes"] = models.Outcome.objects.filter(design__id=self.object.pk)
        context["chemical"] = models.Chemical.objects.filter(design__id=self.object.pk)
        context["criteria"] = models.Criteria.objects.filter(design__id=self.object.pk)
        context["exposure_levels"] = models.ExposureLevel.objects.filter(design__id=self.object.pk)
        context["adjustment_factors"] = models.AdjustmentFactor.objects.filter(design__id=self.object.pk)
        context["data_extractions"] = models.DataExtraction.objects.filter(design__id=self.object.pk)
        return context


class DesignDetail(BaseDetail):
    model = models.Design

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exposures"] = models.Exposure.objects.filter(design__id=self.object.pk)
        context["outcomes"] = models.Outcome.objects.filter(design__id=self.object.pk)
        context["chemical"] = models.Chemical.objects.filter(design__id=self.object.pk)
        context["criteria"] = models.Criteria.objects.filter(design__id=self.object.pk)
        context["exposure_levels"] = models.ExposureLevel.objects.filter(design__id=self.object.pk)
        context["adjustment_factors"] = models.AdjustmentFactor.objects.filter(design__id=self.object.pk)
        context["data_extractions"] = models.DataExtraction.objects.filter(design__id=self.object.pk)
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
    form_fragment = "epiv2/components/design_form_copy.html"
    detail_fragment = "epiv2/components/design_detail_frag.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = forms.DesignForm(request.POST, parent=request.item.parent)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
        else:
            form = forms.DesignForm()
        context = self.get_context_data(form=form)
        return render(request, template, context)

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

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            self.perform_delete(request.item)
            return self.str_response()
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())


# Criteria viewset
class CriteriaViewset(HtmxViewSet):
    actions = {"create", "read", "update", "delete", "clone"}
    parent_model = models.Design
    model = models.Criteria
    form_fragment = "epiv2/components/criteria_edit_row.html"
    detail_fragment = "epiv2/components/criteria_row.html"

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
            self.perform_delete(request.item)
            return self.str_response()
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
    form_fragment = "epiv2/components/chemical_edit_row.html"
    detail_fragment = "epiv2/components/chemical_row.html"

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
            self.perform_delete(request.item)
            return self.str_response()
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
    form_fragment = "epiv2/components/exposure_edit_row.html"
    detail_fragment = "epiv2/components/exposure_row.html"

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
            self.perform_delete(request.item)
            return self.str_response()
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
    form_fragment = "epiv2/components/exposurelevel_edit_row.html"
    detail_fragment = "epiv2/components/exposurelevel_row.html"

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
            self.perform_delete(request.item)
            return self.str_response()
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
    form_fragment = "epiv2/components/outcome_edit_row.html"
    detail_fragment = "epiv2/components/outcome_row.html"

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
            self.perform_delete(request.item)
            return self.str_response()
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
    form_fragment = "epiv2/components/adjustment_factor_edit_row.html"
    detail_fragment = "epiv2/components/adjustment_factor_row.html"

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
            self.perform_delete(request.item)
            return self.str_response()
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
    form_fragment = "epiv2/components/data_extraction_edit_row.html"
    detail_fragment = "epiv2/components/data_extraction_row.html"

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
            self.perform_delete(request.item)
            return self.str_response()
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())
