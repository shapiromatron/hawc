import json

from django.db.models import Q
from django.db.models.loading import get_model
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponseRedirect, HttpResponseNotAllowed
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, ListView, DetailView, TemplateView, FormView
from django.views.generic.edit import CreateView
from django.shortcuts import HttpResponse, get_object_or_404

from utils.views import (MessageMixin, LoginRequiredMixin, BaseCreate,
                         CloseIfSuccessMixin, BaseDetail, BaseUpdate,
                         BaseDelete, BaseVersion, BaseList)

from celery import chain

from . import forms, models, tasks


# General views
class Home(TemplateView):
    template_name = 'hawc/home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse_lazy('portal'))
        return super(Home, self).get(request, *args, **kwargs)


class About(TemplateView):
    template_name = 'hawc/about.html'


class Contact(MessageMixin, FormView):
    template_name = 'hawc/contact.html'
    form_class = forms.ContactForm
    success_url = reverse_lazy('home')
    success_message = 'Your message has been sent!'

    def get_form_kwargs(self):
        kwargs = super(Contact, self).get_form_kwargs()
        kwargs['back_href'] = self.request.META.get(
            'HTTP_REFERER', reverse('portal'))
        return kwargs

    def form_valid(self, form):
        form.send_email()
        return super(Contact, self).form_valid(form)


class Error403(TemplateView):
    template_name = '403.html'


class Error404(TemplateView):
    template_name = '404.html'


class Error500(TemplateView):
    template_name = '500.html'


# Assessment Object
class AssessmentList(LoginRequiredMixin, ListView):
    model = models.Assessment
    template_name = "assessment/assessment_home.html"


class AssessmentFullList(LoginRequiredMixin, ListView):
    model = models.Assessment

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AssessmentFullList, self).dispatch(request, *args, **kwargs)


class AssessmentPublicList(ListView):
    model = models.Assessment

    def get_queryset(self):
        return self.model.objects.filter(
            public=True,
            hide_from_public_page=False
        ).order_by('name')


class AssessmentCreate(LoginRequiredMixin, MessageMixin, CreateView):
    success_message = 'Assessment created.'
    model = models.Assessment
    form_class = forms.AssessmentForm


class AssessmentRead(BaseDetail):
    model = models.Assessment

    def get_context_data(self, **kwargs):
        context = super(AssessmentRead, self).get_context_data(**kwargs)
        context['comment_object_type'] = "assessment"
        context['comment_object_id'] = self.object.pk
        return context


class AssessmentUpdate(BaseUpdate):
    success_message = 'Assessment updated.'
    model = models.Assessment
    form_class = forms.AssessmentForm


class AssessmentModulesUpdate(AssessmentUpdate):
    success_message = 'Assessment modules updated.'
    form_class = forms.AssessmentModulesForm
    template_name = "assessment/assessment_module_form.html"


class AssessmentDelete(BaseDelete):
    model = models.Assessment
    success_url = reverse_lazy('portal')
    success_message = 'Assessment deleted.'


class AssessmentVersions(BaseVersion):
    model = models.Assessment
    template_name = "assessment/assessment_versions.html"


class AssessmentReports(BaseList):
    """
    Download assessment-level Microsoft Word reports.
    """
    parent_model = models.Assessment
    model = models.ReportTemplate
    template_name = "assessment/assessment_reports.html"

    def get_queryset(self):
        # Get report-templates associated with no assessment (global) and
        # those associated with selected assessment
        return self.model.objects.filter(
            Q(assessment=None) | Q(assessment=self.assessment))

    def get_context_data(self, **kwargs):
        context = super(AssessmentReports, self).get_context_data(**kwargs)
        context['report_types'] = self.model.get_by_report_type(self.object_list)
        return context


class AssessmentDownloads(BaseDetail):
    """
    Download assessment-level Microsoft Excel reports
    """
    model = models.Assessment
    template_name = "assessment/assessment_downloads.html"


class AssessmentEmailManagers(MessageMixin, FormView):
    template_name = 'assessment/assessment_email_managers.html'
    form_class = forms.AssessmentEmailManagersForm
    success_message = 'Your message has been sent!'

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        self.assessment = get_object_or_404(models.Assessment, pk=kwargs.get('pk'))
        return super(AssessmentEmailManagers, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AssessmentEmailManagers, self).get_form_kwargs()
        kwargs['assessment'] = self.assessment
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AssessmentEmailManagers, self).get_context_data(**kwargs)
        context['object'] = self.assessment
        return context

    def get_success_url(self):
        return self.assessment.get_absolute_url()

    def form_valid(self, form):
        form.send_email()
        return super(AssessmentEmailManagers, self).form_valid(form)


# Word Templates
class ReportTemplateCreate(BaseCreate):
    success_message = 'Report template created.'
    parent_model = models.Assessment
    model = models.ReportTemplate
    form_class = forms.ReportTemplateForm


class ReportTemplateList(BaseList):
    parent_model = models.Assessment
    model = models.ReportTemplate

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)


class ReportTemplateDetail(BaseDetail):
    model = models.ReportTemplate


class ReportTemplateUpdate(BaseUpdate):
    success_message = "Report template updated."
    model = models.ReportTemplate
    form_class = forms.ReportTemplateForm


class ReportTemplateDelete(BaseDelete):
    success_message = "Report template deleted."
    model = models.ReportTemplate

    def get_success_url(self):
        return reverse_lazy("assessment:template_list", kwargs={"pk": self.assessment.pk})


# Endpoint objects
class EndpointJSON(BaseDetail):
    model = models.BaseEndpoint

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return HttpResponse(self.object.get_json(), content_type="application/json")


class EffectTagCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = 'Effect tag created.'
    parent_model = models.Assessment
    parent_template_name = 'assessment'
    model = models.EffectTag
    form_class = forms.EffectTagForm


class BaseEndpointList(BaseList):
    parent_model = models.Assessment
    model = models.BaseEndpoint

    def get_context_data(self, **kwargs):
        context = super(BaseEndpointList, self).get_context_data(**kwargs)

        eps = self.model.endpoint\
            .related.model.objects\
            .filter(assessment_id=self.assessment.id)\
            .count()

        aos = self.model.assessedoutcome\
            .related.model.objects\
            .filter(assessment_id=self.assessment.id)\
            .count()

        mrs = get_model('epi', 'metaresult')\
            .objects\
            .filter(protocol__study__assessment_id=self.assessment.id)\
            .count()

        iveps = self.model.ivendpoint\
            .related.model.objects\
            .filter(assessment_id=self.assessment.id)\
            .count()

        alleps = eps + aos + mrs + iveps

        context.update({
            "ivendpoints": iveps,
            "endpoints": eps,
            "assessed_outcomes": aos,
            "meta_results": mrs,
            "total_endpoints": alleps
        })

        return context


# Changelog views
class ChangeLogList(ListView):
    model = models.ChangeLog
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ChangeLogList, self).get_context_data(**kwargs)
        if self.request.GET.get('detailed'):
            context['detailed'] = True
        return context


class ChangeLogDetail(DetailView):
    model = models.ChangeLog


# Assorted functionality
class CASDetails(TemplateView):

    def get(self, request, *args, **kwargs):
        cas = self.request.GET.get('cas')
        task = tasks.get_chemspider_details.delay(cas)
        v = task.get(timeout=60)
        if v:
            return HttpResponse(json.dumps(v),
                                content_type="application/json")


class CloseWindow(TemplateView):
    template_name = "hawc/close_window.html"


class UpdateSession(View):

    http_method_names = (u'post', )

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseNotAllowed(['POST'])
        request.session['hideSidebar'] = request.POST.get("hideSidebar", "true") == "true"
        return HttpResponse(True)


@csrf_exempt  # todo: get rid of this! update page to use csrf.js
def download_plot(request):
    if request.method == 'POST':

        # default response
        response = HttpResponse("<p>An error in processing occurred.</p>")

        # grab input values and create converter object
        output_type = request.POST.get('output', None)
        svg = request.POST['svg']
        url = request.META['HTTP_REFERER']
        width = int(float(request.POST['width'])*5)
        height = int(float(request.POST['height'])*5)
        converter = tasks.SVGConverter(svg, url, width, height)

        if output_type == 'svg':
            svg = converter.get_svg()
            response = HttpResponse(svg, content_type="image/svg+xml")
            response['Content-Disposition'] = 'attachment; filename="download.svg"'

        elif output_type == 'png':
            task = converter.convert_to_png.delay(converter)
            output = task.get(timeout=60)
            if output:
                response = HttpResponse(output, content_type="image/png")
                response['Content-Disposition'] = 'attachment; filename="download.png"'

        elif output_type == 'pptx':
            task = chain(
                converter.convert_to_png.s(converter, delete_and_return_object=False),
                converter.convert_to_pptx.s()
            )()
            output = task.get(timeout=90)
            if output:
                response = HttpResponse(output, content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
                response['Content-Disposition'] = 'attachment; filename="download.pptx"'

        elif output_type == 'pdf':
            task = converter.convert_to_pdf.delay(converter)
            output = task.get(timeout=60)
            if output:
                response = HttpResponse(output, content_type="application/pdf")
                response['Content-Disposition'] = 'attachment; filename="download.pdf"'

        else:
            response = HttpResponse("<p>An error in processing occurred - unknown output type.</p>")

        return response
    else:
        raise Http404
