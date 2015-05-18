import json

from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, FormView

from assessment.models import Assessment
from utils.helper import HAWCDjangoJSONEncoder
from utils.views import (AssessmentPermissionsMixin, BaseList, BaseCreate,
                         BaseDetail, BaseUpdate, BaseDelete)

from . import forms, models


# SUMMARY-TEXT
class SummaryTextJSON(BaseDetail):
    model = models.SummaryText

    def dispatch(self, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=kwargs.get('pk'))
        self.permission_check_user_can_view()
        return super(SummaryTextJSON, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        content = self.model.get_all_tags(self.assessment, json_encode=True)
        return HttpResponse(content, content_type="application/json")


class SummaryTextList(BaseList):
    parent_model = Assessment
    model = models.SummaryText

    def get_queryset(self):
        rt = self.model.get_assessment_root_node(assessment=self.assessment)
        return self.model.objects.filter(pk__in=[rt.pk])


class SummaryTextModify(BaseCreate):
    # handles Create, Update, Delete for Summary Text
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.SummaryText
    form_class = forms.SummaryTextForm

    def post(self, request, *args, **kwargs):
        status = "fail"
        result = []
        if request.is_ajax() and request.user.is_authenticated():
            try:
                post = self.request.POST.copy()
                post.pop('csrfmiddlewaretoken')
                post.pop('_wysihtml5_mode', None)
                post['assessment'] = self.assessment
                existing_id = int(post.pop(u'id', -1)[0])
                delete = post.pop(u'delete', [False])[0]

                if int(post.get('sibling', -1))>0:
                    post['sibling'] = get_object_or_404(self.model, pk=post['sibling'])
                    post.pop('parent')
                else:
                    post.pop('sibling')

                if int(post.get('parent', -1))>0:
                    post['parent'] = get_object_or_404(self.model, pk=post['parent'])
                else:
                    post.pop('parent', None)

                if existing_id>0:
                    obj = get_object_or_404(self.model, pk=existing_id)
                    if delete:
                        obj.delete()
                    else:
                        if obj.assessment != self.assessment:
                            raise Exception("Selected object is not from the same assessment")
                        obj.modify(**post)
                else:
                    self.model.add_summarytext(**post)

                status = "ok"
                result = self.model.get_all_tags(self.assessment, json_encode=False)
            except Exception as e:
                result.append(unicode(e))

        response = {"status": status, "content": result}
        return HttpResponse(json.dumps(response, cls=HAWCDjangoJSONEncoder),
                            content_type="application/json")


# VISUALIZATIONS
class VisualizationList(BaseList):
    parent_model = Assessment
    model = models.Visual

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)


class VisualizationDetail(BaseDetail):
    model = models.Visual


class VisualizationCreateSelector(BaseDetail):
    model = Assessment
    template_name = "summary/visual_selector.html"


class VisualizationCreate(BaseCreate):
    success_message = "Visualization created."
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.Visual

    def get_form_class(self):
        visual_type = int(self.kwargs.get('visual_type'))
        try:
            return forms.get_visual_form(visual_type)
        except ValueError:
            raise Http404

    def get_form_kwargs(self):
        kwargs = super(VisualizationCreate, self).get_form_kwargs()
        kwargs['visual_type'] = int(self.kwargs.get('visual_type'))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(VisualizationCreate, self).get_context_data(**kwargs)
        context['visual_type'] = int(self.kwargs.get('visual_type'))
        return context


class VisualizationCreateTester(VisualizationCreate):
    parent_model = Assessment
    http_method_names = ('post', )

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        response = form.instance.get_editing_dataset(request)
        return HttpResponse(response, content_type="application/json")


class VisualizationUpdate(BaseUpdate):
    success_message = 'Visualization updated.'
    model = models.Visual

    def get_form_class(self):
        try:
            return forms.get_visual_form(self.object.visual_type)
        except ValueError:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(VisualizationUpdate, self).get_context_data(**kwargs)
        context['visual_type'] = self.object.visual_type
        return context


class VisualizationDelete(BaseDelete):
    success_message = 'Visualization deleted.'
    model = models.Visual

    def get_success_url(self):
        return reverse_lazy('summary:visualization_list', kwargs={'pk': self.assessment.pk})


# DATA-PIVOT
class GeneralDataPivot(TemplateView):
    """
    Generalized meta-data viewer, not tied to any assessment. No persistence.
    Used to upload raw CSV data from a file.
    """
    template_name = "summary/datapivot_general.html"


class ExcelUnicode(TemplateView):
    template_name = "summary/datapivot_save_as_unicode_modal.html"


class DataPivotNewPrompt(TemplateView):
    """
    Select if you wish to upload a file or use a query.
    """
    model = models.DataPivot
    crud = 'Read'
    template_name = 'summary/datapivot_type_selector.html'

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
    template_name = 'summary/datapivot_form.html'

    def get_success_url(self):
        return reverse_lazy('summary:dp_update',
                             kwargs={'pk': self.assessment.pk,
                                     'slug': self.object.slug})

    def get_form_kwargs(self):
        kwargs = super(DataPivotNew, self).get_form_kwargs()

        # check if we have a template to use
        try:
            pk = int(self.request.GET.get('initial'))
        except Exception:
            pk = None

        if pk:
            obj = self.model.objects.filter(pk=pk).first()
            if obj and obj.get_assessment() == self.assessment:
                kwargs['instance'] = obj

        return kwargs


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

    def get_form_kwargs(self):
        kwargs = super(DataPivotFileNew, self).get_form_kwargs()
        if kwargs.get('instance'):
            # TODO: get file to copy properly when copying from existing
            kwargs['instance'].file = None
        return kwargs


class DataPivotCopyAsNewSelector(BaseDetail):
    # Select an existing assessed outcome as a template for a new one
    model = Assessment
    template_name = 'summary/datapivot_copy_selector.html'

    def get_context_data(self, **kwargs):
        context = super(DataPivotCopyAsNewSelector, self).get_context_data(**kwargs)
        context['form'] = forms.DataPivotSelectorForm(assessment_id=self.assessment.pk)
        return context

    def post(self, request, *args, **kwargs):
        self.object = super(DataPivotCopyAsNewSelector, self).get_object()
        dp = get_object_or_404(models.DataPivot, pk=self.request.POST.get('dp'))
        if hasattr(dp, 'datapivotupload'):
            url = reverse_lazy('summary:dp_new-file', kwargs={"pk": self.assessment.pk})
        else:
            url = reverse_lazy('summary:dp_new-query', kwargs={"pk": self.assessment.pk})

        url += "?initial={0}".format(dp.pk)
        return HttpResponseRedirect(url)


class GetDataPivotObjectMixin(object):

    def get_object(self):
        slug = self.kwargs.get('slug')
        assessment = self.kwargs.get('pk')
        obj = get_object_or_404(models.DataPivot, assessment=assessment, slug=slug)
        if hasattr(obj, "datapivotquery"):
            obj = obj.datapivotquery
        else:
            obj = obj.datapivotupload
        return super(GetDataPivotObjectMixin, self).get_object(object=obj)


class DataPivotDetail(GetDataPivotObjectMixin, BaseDetail):
    model = models.DataPivot
    template_name = "summary/datapivot_detail.html"


class DataPivotData(GetDataPivotObjectMixin, BaseDetail):
    model = models.DataPivot

    def get_export_format(self):
        format_ = self.request.GET.get("format", "excel")
        if format_ not in ["tsv", "excel"]:
            raise Http404()
        return format_

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        format_ = self.get_export_format()
        return self.object.get_dataset(format_)


class DataPivotUpdateSettings(GetDataPivotObjectMixin, BaseUpdate):
    success_message = 'Data Pivot updated.'
    model = models.DataPivot
    form_class = forms.DataPivotSettingsForm
    template_name = 'summary/datapivot_update_settings.html'


class DataPivotUpdateQuery(GetDataPivotObjectMixin, BaseUpdate):
    success_message = 'Data Pivot updated.'
    model = models.DataPivotQuery
    form_class = forms.DataPivotQueryForm
    template_name = 'summary/datapivot_form.html'

    def get_context_data(self, **kwargs):
        context = super(DataPivotUpdateQuery, self).get_context_data(**kwargs)
        context['file_loader'] = False
        return context


class DataPivotUpdateFile(GetDataPivotObjectMixin, BaseUpdate):
    success_message = 'Data Pivot updated.'
    model = models.DataPivotUpload
    form_class = forms.DataPivotUploadForm
    template_name = 'summary/datapivot_form.html'

    def get_context_data(self, **kwargs):
        context = super(DataPivotUpdateFile, self).get_context_data(**kwargs)
        context['file_loader'] = True
        return context


class DataPivotDelete(GetDataPivotObjectMixin, BaseDelete):
    success_message = 'Data Pivot deleted.'
    model = models.DataPivot
    template_name = "summary/datapivot_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy('summary:visualization_list', kwargs={'pk': self.assessment.pk})


class DataPivotSearch(AssessmentPermissionsMixin, FormView):
    """ Returns JSON representations from data pivot search. POST only."""
    form_class = forms.DataPivotSearchForm

    def dispatch(self, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=kwargs['pk'])
        self.permission_check_user_can_view()
        return super(DataPivotSearch, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_form_kwargs(self):
        kwargs = super(FormView, self).get_form_kwargs()
        kwargs['assessment'] = self.assessment
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
