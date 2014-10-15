import json

from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, TemplateView, FormView

from assessment.models import Assessment
from utils.views import (AssessmentPermissionsMixin, CanCreateMixin,
                         MessageMixin, BaseList, BaseCreate, BaseDetail,
                         BaseUpdate, BaseDelete)
from utils.helper import HAWCDjangoJSONEncoder

from . import forms
from . import models


class GeneralDataPivot(TemplateView):
    """
    Generalized meta-data viewer, not tied to any assessment. No persistence.
    Used to upload raw CSV data from a file.
    """
    template_name = "data_pivot/datapivot_general.html"


class ExcelUnicode(TemplateView):
    template_name = "data_pivot/_save_as_unicode_modal.html"


class DataPivotList(BaseList):
    parent_model = Assessment
    model = models.DataPivot

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)


class DataPivotNewPrompt(TemplateView):
    """
    Select if you wish to upload a file or use a query.
    """
    model = models.DataPivot
    crud = 'Read'
    template_name = 'data_pivot/datapivot_type_selector.html'

    def dispatch(self, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=kwargs['pk'])
        return super(DataPivotNewPrompt, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        return context


class DataPivotNew(BaseCreate):
    # abstract view; extended below for actual use
    parent_model = Assessment
    parent_template_name = 'assessment'
    success_message = 'Data Pivot created.'
    template_name = 'data_pivot/datapivot_form.html'

    def get_success_url(self):
        return reverse_lazy('data_pivot:update',
                             kwargs={'assessment': self.assessment.pk,
                                     'slug': self.object.slug})


class DataPivotQueryNew(DataPivotNew):
    model = models.DataPivotQuery
    form_class = forms.DataPivotQueryForm

    def get_context_data(self, **kwargs):
        context = super(DataPivotQueryNew, self).get_context_data(**kwargs)
        context['file_loader'] = False
        return context


class DataPivotFileNew(DataPivotNew):
    model = models.DataPivotUpload
    form_class = forms.DataPivotUploadForm

    def get_context_data(self, **kwargs):
        context = super(DataPivotFileNew, self).get_context_data(**kwargs)
        context['file_loader'] = True
        return context


class DataPivotDetail(BaseDetail):
    model = models.DataPivot


class DataPivotJSON(BaseDetail):
    model = models.DataPivot

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return HttpResponse(self.object.get_json(), content_type="application/json")


class DataPivotUpdateSettings(BaseUpdate):
    success_message = 'Data Pivot updated.'
    model = models.DataPivot
    form_class = forms.DataPivotSettingsForm
    template_name = 'data_pivot/datapivot_update_settings.html'


class DataPivotUpdateQuery(BaseUpdate):
    success_message = 'Data Pivot updated.'
    model = models.DataPivotQuery
    form_class = forms.DataPivotQueryForm
    template_name = 'data_pivot/datapivot_form.html'

    def get_context_data(self, **kwargs):
        context = super(DataPivotUpdateQuery, self).get_context_data(**kwargs)
        context['file_loader'] = False
        return context


class DataPivotUpdateFile(BaseUpdate):
    success_message = 'Data Pivot updated.'
    model = models.DataPivotUpload
    form_class = forms.DataPivotUploadForm
    template_name = 'data_pivot/datapivot_form.html'

    def get_context_data(self, **kwargs):
        context = super(DataPivotUpdateFile, self).get_context_data(**kwargs)
        context['file_loader'] = True
        return context


class DataPivotDelete(BaseDelete):
    success_message = 'Data Pivot deleted.'
    model = models.DataPivot

    def get_success_url(self):
        return reverse_lazy('data_pivot:list', kwargs={'pk': self.assessment.pk})


class DataPivotSearch(AssessmentPermissionsMixin, FormView):
    """ Returns JSON representations from data pivot search. POST only."""
    form_class = forms.DataPivotSearchForm

    def dispatch(self, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=kwargs['assessment'])
        self.permission_check_user_can_view()
        return super(DataPivotSearch, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_form_kwargs(self):
        kwargs = super(FormView, self).get_form_kwargs()
        kwargs['assessment_pk'] = self.assessment.pk
        return kwargs

    def form_invalid(self, form):
        return HttpResponse(json.dumps({"status": "fail",
                                        "dps": [],
                                        "error": "invalid form format"}),
                            content_type="application/json")

    def form_valid(self, form):
        dps = form.search()
        return HttpResponse(json.dumps({"status": "success",
                                        "dps": dps},
                                       cls=HAWCDjangoJSONEncoder),
                            content_type="application/json")
