import json

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.apps import apps
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponseNotAllowed
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, ListView, DetailView, TemplateView, FormView
from django.views.generic.edit import CreateView
from django.shortcuts import HttpResponse, get_object_or_404

from utils.views import (MessageMixin, LoginRequiredMixin, BaseCreate,
                         CloseIfSuccessMixin, BaseDetail, BaseUpdate,
                         BaseDelete, BaseList, TeamMemberOrHigherMixin,
                         ProjectManagerOrHigherMixin)
from utils.helper import tryParseInt

from . import forms, models, tasks, serializers


# General views
class Home(TemplateView):
    template_name = 'hawc/home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse_lazy('portal'))
        return super(Home, self).get(request, *args, **kwargs)


class About(TemplateView):
    template_name = 'hawc/about.html'

    def get_context_data(self, **kwargs):
        context = super(About, self).get_context_data(**kwargs)
        context['object_list'] = models.ChangeLog.objects.all()[:5]
        context['GIT_COMMIT'] = settings.GIT_COMMIT
        context['COMMIT_URL'] = settings.COMMIT_URL
        return context


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
        return self.model.objects.get_public_assessments()


class AssessmentCreate(LoginRequiredMixin, MessageMixin, CreateView):
    success_message = 'Assessment created.'
    model = models.Assessment
    form_class = forms.AssessmentForm


class AssessmentRead(BaseDetail):
    model = models.Assessment

    def get_context_data(self, **kwargs):
        context = super(AssessmentRead, self).get_context_data(**kwargs)
        context['attachments'] = models.Attachment.objects.get_attachments(
            self.object,
            not context['obj_perms']['edit']
        )
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
        return self.model.objects.with_global(self.assessment)

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


# Attachment views
class AttachmentCreate(BaseCreate):
    success_message = 'Attachment added.'
    parent_model = models.Assessment
    parent_template_name = 'parent'
    model = models.Attachment
    form_class = forms.AttachmentForm

    def get_success_url(self):
        return self.object.get_absolute_url()


class AttachmentRead(BaseDetail):
    model = models.Attachment

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.assessment.user_can_view_attachments(self.request.user):
            return HttpResponseRedirect(self.object.attachment.url)
        else:
            return PermissionDenied


class AttachmentUpdate(BaseUpdate):
    success_message = 'Assessment updated.'
    model = models.Attachment
    form_class = forms.AttachmentForm


class AttachmentDelete(BaseDelete):
    success_message = 'Attachment deleted.'
    model = models.Attachment

    def get_success_url(self):
        return self.object.get_absolute_url()


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
        return self.model.objects.get_qs(self.assessment)


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
class EffectTagCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = 'Effect tag created.'
    parent_model = models.Assessment
    parent_template_name = 'assessment'
    model = models.EffectTag
    form_class = forms.EffectTagForm


class getStrains(TemplateView):
    # Return the valid strains for the requested species in JSON

    def get(self, request, *args, **kwargs):
        strains = []
        try:
            sp = models.Species.objects.get(pk=request.GET.get('species'))
            strains = list(models.Strain.objects.filter(species=sp).values('id', 'name'))
        except:
            pass
        return HttpResponse(json.dumps(strains), content_type="application/json")


class SpeciesCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = 'Species created.'
    parent_model = models.Assessment
    parent_template_name = 'assessment'
    model = models.Species
    form_class = forms.SpeciesForm


class StrainCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = 'Strain created.'
    parent_model = models.Assessment
    parent_template_name = 'assessment'
    model = models.Strain
    form_class = forms.StrainForm


class DoseUnitsCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = 'Dose units created.'
    parent_model = models.Assessment
    parent_template_name = 'assessment'
    model = models.DoseUnits
    form_class = forms.DoseUnitsForm


class BaseEndpointList(BaseList):
    parent_model = models.Assessment
    model = models.BaseEndpoint

    def get_context_data(self, **kwargs):
        context = super(BaseEndpointList, self).get_context_data(**kwargs)

        eps = self.model.endpoint\
            .related.related_model.objects\
            .get_qs(self.assessment.id)\
            .count()

        os = self.model.outcome\
            .related.related_model.objects\
            .get_qs(self.assessment.id)\
            .count()

        mrs = apps.get_model('epimeta', 'metaresult')\
            .objects\
            .get_qs(self.assessment.id)\
            .count()

        iveps = self.model.ivendpoint\
            .related.related_model.objects\
            .get_qs(self.assessment.id)\
            .count()

        alleps = eps + os + mrs + iveps

        context.update({
            "ivendpoints": iveps,
            "endpoints": eps,
            "outcomes": os,
            "meta_results": mrs,
            "total_endpoints": alleps
        })

        return context


class CleanExtractedData(TeamMemberOrHigherMixin, BaseEndpointList):
    '''
    To add a model to clean,
     - add TEXT_CLEANUP_FIELDS = {...fields} to the model
     - add model count dict to assessment.views.AssessmentEndpointList
     - add model serializer that uses utils.api.DynamicFieldsMixin
     - add api view that inherits from assessment.api.CleanupFieldsBaseViewSet
        with model={model} & serializer_class={new serializer}
     - add url for api view to urls.py
     - add url and model title to templates/assessment/clean_extracted_data.html config object
    '''

    template_name = 'assessment/clean_extracted_data.html'

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.parent_model, pk=kwargs['pk'])


# Changelog views
class ChangeLogList(ListView):
    model = models.ChangeLog
    paginate_by = 30


class ChangeLogDetail(DetailView):
    model = models.ChangeLog


# Assorted functionality
class CASDetails(TemplateView):

    def get(self, request, *args, **kwargs):
        cas = self.request.GET.get('cas')
        task = tasks.get_chemspider_details.delay(cas)
        v = task.get(timeout=60)
        if v is None:
            v = {}
        return HttpResponse(json.dumps(v), content_type="application/json")


class CloseWindow(TemplateView):
    template_name = "hawc/close_window.html"


class UpdateSession(View):

    http_method_names = (u'post', )

    def isTruthy(self, request, field):
        return request.POST.get(field, "true") == "true"

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseNotAllowed(['POST'])
        if request.POST.get("hideSidebar"):
            request.session['hideSidebar'] = self.isTruthy(request, 'hideSidebar')
        if request.POST.get("hideBrowserWarning"):
            request.session['hideBrowserWarning'] = self.isTruthy(request, 'hideBrowserWarning')
        return HttpResponse(True)


class DownloadPlot(FormView):

    http_method_names = [u'post', ]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(DownloadPlot, self).dispatch(*args, **kwargs)

    EXPORT_CROSSWALK = {
        'svg': {
            'fn': tasks.convert_to_svg,
            'ct': 'image/svg+xml',
        },
        'png': {
            'fn': tasks.convert_to_png,
            'ct': 'application/png',
        },
        'pdf': {
            'fn': tasks.convert_to_pdf,
            'ct': 'application/pdf',
        },
        'pptx': {
            'fn': tasks.convert_to_pptx,
            'ct': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # noqa
        },
    }

    def post(self, request, *args, **kwargs):

        # default response
        response = HttpResponse("<p>An error in processing occurred.</p>")

        # grab input values and create converter object
        extension = request.POST.get('output', None)
        svg = request.POST['svg']
        url = request.META['HTTP_REFERER']
        width = int(float(request.POST['width'])*5)
        height = int(float(request.POST['height'])*5)

        handler = self.EXPORT_CROSSWALK.get(extension, None)
        if handler:
            task = handler['fn'].delay(svg, url, width, height)
            output = task.get(timeout=90)
            if output:
                response = HttpResponse(output, content_type=handler['ct'])
                response['Content-Disposition'] = \
                    'attachment; filename="download.{}"'.format(extension)

        return response


class CleanStudyRoB(ProjectManagerOrHigherMixin, BaseDetail):
    template_name = 'assessment/clean_study_rob_scores.html'
    model = models.Assessment

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.model, pk=kwargs['pk'])
