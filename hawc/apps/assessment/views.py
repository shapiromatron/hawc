import json
import logging

from django.apps import apps
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import HttpResponse, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, ListView, TemplateView, View
from django.views.generic.edit import CreateView

from ..common.views import (
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseList,
    BaseUpdate,
    CloseIfSuccessMixin,
    LoginRequiredMixin,
    MessageMixin,
    ProjectManagerOrHigherMixin,
    TeamMemberOrHigherMixin,
    TimeSpentOnPageMixin,
    beta_tester_required,
)
from . import forms, models, serializers, tasks


def percentage(numerator, denominator):
    # Checking for denominator counts that are zero when dividing
    try:
        return numerator / float(denominator)
    except ZeroDivisionError:
        return 0


# General views
class Home(TemplateView):
    template_name = "hawc/home.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("portal"))
        return super().get(request, *args, **kwargs)


class About(TemplateView):
    template_name = "hawc/about.html"

    def get_object_counts(self):
        key = "about-counts"
        counts = cache.get(key)
        if counts is None:

            updated = timezone.now()

            users = apps.get_model("myuser", "HAWCUser").objects.count()

            assessments = models.Assessment.objects.count()

            references = apps.get_model("lit", "Reference").objects.count()

            tags = apps.get_model("lit", "ReferenceTags").objects.count()

            references_tagged = (
                apps.get_model("lit", "ReferenceTags").objects.distinct("content_object_id").count()
            )

            assessments_with_studies = (
                apps.get_model("study", "Study")
                .objects.values_list("assessment_id", flat=True)
                .distinct()
                .count()
            )

            studies = apps.get_model("study", "Study").objects.count()

            rob_scores = apps.get_model("riskofbias", "RiskOfBiasScore").objects.count()

            studies_with_rob = (
                apps.get_model("study", "Study")
                .objects.annotate(robc=Count("riskofbiases"))
                .filter(robc__gt=0)
                .count()
            )

            endpoints = apps.get_model("animal", "Endpoint").objects.count()

            endpoints_with_data = (
                apps.get_model("animal", "EndpointGroup")
                .objects.order_by("endpoint_id")
                .distinct("endpoint_id")
                .count()
            )

            outcomes = apps.get_model("epi", "Outcome").objects.count()

            results = apps.get_model("epi", "Result").objects.count()

            results_with_data = (
                apps.get_model("epi", "GroupResult").objects.distinct("result_id").count()
            )

            iv_endpoints = apps.get_model("invitro", "IVEndpoint").objects.count()

            iv_endpoints_with_data = (
                apps.get_model("invitro", "IVEndpointGroup")
                .objects.order_by("endpoint_id")
                .distinct("endpoint_id")
                .count()
            )

            visuals = (
                apps.get_model("summary", "Visual").objects.count()
                + apps.get_model("summary", "DataPivot").objects.count()
            )

            assessments_with_visuals = len(
                set(
                    models.Assessment.objects.order_by("-created")
                    .annotate(vc=Count("visuals"))
                    .filter(vc__gt=0)
                    .values_list("id", flat=True)
                ).union(
                    set(
                        models.Assessment.objects.order_by("-created")
                        .annotate(dp=Count("datapivot"))
                        .filter(dp__gt=0)
                        .values_list("id", flat=True)
                    )
                )
            )

            counts = dict(
                updated=updated,
                users=users,
                assessments=assessments,
                references=references,
                tags=tags,
                references_tagged=references_tagged,
                references_tagged_percent=percentage(references_tagged, references),
                studies=studies,
                assessments_with_studies=assessments_with_studies,
                assessments_with_studies_percent=percentage(assessments_with_studies, assessments),
                rob_scores=rob_scores,
                studies_with_rob=studies_with_rob,
                studies_with_rob_percent=percentage(studies_with_rob, studies),
                endpoints=endpoints,
                endpoints_with_data=endpoints_with_data,
                endpoints_with_data_percent=percentage(endpoints_with_data, endpoints),
                outcomes=outcomes,
                results=results,
                results_with_data=results_with_data,
                results_with_data_percent=percentage(results_with_data, results),
                iv_endpoints=iv_endpoints,
                iv_endpoints_with_data=iv_endpoints_with_data,
                iv_endpoints_with_data_percent=percentage(iv_endpoints_with_data, iv_endpoints),
                visuals=visuals,
                assessments_with_visuals=assessments_with_visuals,
                assessments_with_visuals_percent=percentage(assessments_with_visuals, assessments),
            )
            cache_duration = 60 * 60 * 24  # one day
            cache.set(key, counts, cache_duration)  # cache for one day
            logging.info("Setting about-page cache")
        return counts

    def get_rob_name(self):
        if settings.HAWC_FLAVOR == "PRIME":
            return models.ROB_NAME_CHOICES_ROB_TEXT
        elif settings.HAWC_FLAVOR == "EPA":
            return models.ROB_NAME_CHOICES_SE_TEXT
        else:
            raise ValueError("Unknown HAWC flavor")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["GIT_COMMIT"] = settings.GIT_COMMIT
        context["COMMIT_URL"] = settings.COMMIT_URL
        context["HAWC_FLAVOR"] = settings.HAWC_FLAVOR
        context["rob_name"] = self.get_rob_name()
        context["counts"] = self.get_object_counts()
        return context


class Contact(LoginRequiredMixin, MessageMixin, FormView):
    template_name = "hawc/contact.html"
    form_class = forms.ContactForm
    success_url = reverse_lazy("home")
    success_message = "Your message has been sent!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            back_href=self.request.META.get("HTTP_REFERER", reverse("portal")),
            user=self.request.user,
        )
        return kwargs

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)


class Error403(TemplateView):
    template_name = "403.html"


class Error404(TemplateView):
    template_name = "404.html"


class Error500(TemplateView):
    template_name = "500.html"


# Assessment Object
class AssessmentList(LoginRequiredMixin, ListView):
    model = models.Assessment
    template_name = "assessment/assessment_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_v2_license"] = not self.request.user.license_v2_accepted
        return context


class AssessmentFullList(LoginRequiredMixin, ListView):
    model = models.Assessment

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class AssessmentPublicList(ListView):
    model = models.Assessment

    def get_queryset(self):
        qs = self.model.objects.get_public_assessments()
        dtxsid = self.request.GET.get("dtxsid")
        if dtxsid:
            qs = qs.filter(dtxsids=dtxsid)
        return qs


class AssessmentCreate(TimeSpentOnPageMixin, LoginRequiredMixin, MessageMixin, CreateView):
    success_message = "Assessment created."
    model = models.Assessment
    form_class = forms.AssessmentForm

    def get_success_url(self):
        self.assessment = self.object
        response = super().get_success_url()
        return response


class AssessmentRead(BaseDetail):
    model = models.Assessment

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related(
            "project_manager", "team_members", "reviewers", "datasets", "dtxsids"
        )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attachments"] = models.Attachment.objects.get_attachments(
            self.object, not context["obj_perms"]["edit"]
        )
        context["dtxsids"] = json.dumps(
            serializers.AssessmentSerializer().to_representation(self.object)["dtxsids"]
        )
        context["datasets"] = (
            context["object"].datasets.all()
            if context["obj_perms"]["edit"]
            else context["object"].datasets.filter(published=True)
        )
        return context


class AssessmentUpdate(BaseUpdate):
    success_message = "Assessment updated."
    model = models.Assessment
    form_class = forms.AssessmentForm


class AssessmentModulesUpdate(AssessmentUpdate):
    success_message = "Assessment modules updated."
    form_class = forms.AssessmentModulesForm
    template_name = "assessment/assessment_module_form.html"


class AssessmentDelete(BaseDelete):
    model = models.Assessment
    success_url = reverse_lazy("portal")
    success_message = "Assessment deleted."


class AssessmentClearCache(MessageMixin, View):
    model = models.Assessment
    success_message = "Assessment cache cleared."

    def get(self, request, *args, **kwargs):
        assessment = get_object_or_404(self.model, pk=kwargs["pk"])
        url = self.request.META.get("HTTP_REFERER", assessment.get_absolute_url())
        if not assessment.user_can_edit_object(request.user):
            raise PermissionDenied()

        assessment.bust_cache()
        self.send_message()
        return HttpResponseRedirect(url)


class AssessmentDownloads(BaseDetail):
    """
    Download assessment-level Microsoft Excel reports
    """

    model = models.Assessment
    template_name = "assessment/assessment_downloads.html"


# Attachment views
class AttachmentCreate(BaseCreate):
    success_message = "Attachment added."
    parent_model = models.Assessment
    parent_template_name = "parent"
    model = models.Attachment
    form_class = forms.AttachmentForm


class AttachmentRead(BaseDetail):
    model = models.Attachment

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.assessment.user_is_part_of_team(self.request.user):
            return HttpResponseRedirect(self.object.attachment.url)
        else:
            return PermissionDenied


class AttachmentUpdate(BaseUpdate):
    success_message = "Assessment updated."
    model = models.Attachment
    form_class = forms.AttachmentForm


class AttachmentDelete(BaseDelete):
    success_message = "Attachment deleted."
    model = models.Attachment

    def get_success_url(self):
        return self.object.get_absolute_url()


# Dataset views
class DatasetCreate(BaseCreate):
    success_message = "Dataset created."
    parent_model = models.Assessment
    parent_template_name = "parent"
    model = models.Dataset
    form_class = forms.DatasetForm


class DatasetRead(BaseDetail):
    model = models.Dataset

    def get_object(self, **kwargs):
        obj = super().get_object(**kwargs)
        if not obj.user_can_view(self.request.user):
            raise PermissionDenied()
        return obj


class DatasetUpdate(BaseUpdate):
    success_message = "Dataset updated."
    model = models.Dataset
    form_class = forms.DatasetForm


class DatasetDelete(BaseDelete):
    success_message = "Dataset deleted."
    model = models.Dataset

    def get_success_url(self):
        return self.object.assessment.get_absolute_url()


# Vocab views
class VocabList(TeamMemberOrHigherMixin, TemplateView):
    template_name = "assessment/vocab.html"

    def get_assessment(self, *args, **kwargs):
        return get_object_or_404(models.Assessment, pk=kwargs["pk"])

    def get_context_data(self, **kwargs):
        Term = apps.get_model("vocab", "Term")
        context = super().get_context_data(**kwargs)
        context["systems"] = Term.objects.assessment_systems(self.assessment.id).order_by(
            "-deprecated_on", "id"
        )
        context["organs"] = Term.objects.assessment_organs(self.assessment.id).order_by(
            "-deprecated_on", "id"
        )
        context["effects"] = Term.objects.assessment_effects(self.assessment.id).order_by(
            "-deprecated_on", "id"
        )
        context["effect_subtypes"] = Term.objects.assessment_effect_subtypes(
            self.assessment.id
        ).order_by("-deprecated_on", "id")
        context["endpoint_names"] = Term.objects.assessment_endpoint_names(
            self.assessment.id
        ).order_by("-deprecated_on", "id")
        return context


# Endpoint objects
class EffectTagCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = "Effect tag created."
    parent_model = models.Assessment
    parent_template_name = "assessment"
    model = models.EffectTag
    form_class = forms.EffectTagForm


class getStrains(TemplateView):
    # Return the valid strains for the requested species in JSON

    def get(self, request, *args, **kwargs):
        strains = []
        try:
            sp = models.Species.objects.get(pk=request.GET.get("species"))
            strains = list(models.Strain.objects.filter(species=sp).values("id", "name"))
        except Exception:
            pass
        return HttpResponse(json.dumps(strains), content_type="application/json")


class SpeciesCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = "Species created."
    parent_model = models.Assessment
    parent_template_name = "assessment"
    model = models.Species
    form_class = forms.SpeciesForm


class StrainCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = "Strain created."
    parent_model = models.Assessment
    parent_template_name = "assessment"
    model = models.Strain
    form_class = forms.StrainForm


class DoseUnitsCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = "Dose units created."
    parent_model = models.Assessment
    parent_template_name = "assessment"
    model = models.DoseUnits
    form_class = forms.DoseUnitsForm


class DSSToxCreate(CloseIfSuccessMixin, LoginRequiredMixin, MessageMixin, CreateView):
    success_message = "DTXSID created."
    model = models.DSSTox
    form_class = forms.DSSToxForm


class BaseEndpointList(BaseList):
    parent_model = models.Assessment
    model = models.BaseEndpoint

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        eps = self.model.endpoint.related.related_model.objects.get_qs(self.assessment.id).count()

        os = self.model.outcome.related.related_model.objects.get_qs(self.assessment.id).count()

        mrs = apps.get_model("epimeta", "metaresult").objects.get_qs(self.assessment.id).count()

        iveps = self.model.ivendpoint.related.related_model.objects.get_qs(
            self.assessment.id
        ).count()

        alleps = eps + os + mrs + iveps

        context.update(
            {
                "ivendpoints": iveps,
                "endpoints": eps,
                "outcomes": os,
                "meta_results": mrs,
                "total_endpoints": alleps,
            }
        )

        return context


class CleanExtractedData(TeamMemberOrHigherMixin, BaseEndpointList):
    """
    To add a model to clean,
     - add TEXT_CLEANUP_FIELDS = {...fields} to the model
     - add model count dict to assessment.views.Assessment.endpoints
     - add model serializer that uses utils.api.DynamicFieldsMixin
     - add api view that inherits from assessment.api.CleanupFieldsBaseViewSet
        with model={model} & serializer_class={new serializer}
     - add url for api view to urls.py
     - add url and model title to templates/assessment/clean_extracted_data.html config object
    """

    template_name = "assessment/clean_extracted_data.html"

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.parent_model, pk=kwargs["pk"])


# Assorted functionality
class CloseWindow(TemplateView):
    template_name = "hawc/close_window.html"


class UpdateSession(View):

    http_method_names = ("post",)

    def isTruthy(self, request, field):
        return request.POST.get(field, "true") == "true"

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseNotAllowed(["POST"])
        if request.POST.get("hideSidebar"):
            request.session["hideSidebar"] = self.isTruthy(request, "hideSidebar")
        return HttpResponse(True)


class DownloadPlot(FormView):

    http_method_names = [
        "post",
    ]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    EXPORT_CROSSWALK = {
        "svg": {"fn": tasks.convert_to_svg, "ct": "image/svg+xml"},
        "png": {"fn": tasks.convert_to_png, "ct": "application/png"},
        "pdf": {"fn": tasks.convert_to_pdf, "ct": "application/pdf"},
        "pptx": {
            "fn": tasks.convert_to_pptx,
            "ct": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        },
    }

    def post(self, request, *args, **kwargs):

        # default response
        response = HttpResponse("<p>An error in processing occurred.</p>")

        # grab input values and create converter object
        extension = request.POST.get("output", None)
        svg = request.POST["svg"]
        url = request.META["HTTP_REFERER"]
        width = int(float(request.POST["width"]) * 5)
        height = int(float(request.POST["height"]) * 5)

        handler = self.EXPORT_CROSSWALK.get(extension, None)
        if handler:
            task = handler["fn"].delay(svg, url, width, height)
            output = task.get(timeout=90)
            if output:
                response = HttpResponse(output, content_type=handler["ct"])
                response["Content-Disposition"] = f'attachment; filename="download.{extension}"'

        return response


class CleanStudyRoB(ProjectManagerOrHigherMixin, BaseDetail):
    template_name = "assessment/clean_study_rob_scores.html"
    model = models.Assessment

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.model, pk=kwargs["pk"])


class AdminDashboard(TemplateView):
    template_name = "admin/dashboard.html"

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AdminAssessmentSize(TemplateView):
    template_name = "admin/assessment-size.html"

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class Healthcheck(View):
    """
    Healthcheck view check; ensure django server can serve requests.
    """

    def get(self, request, *args, **kwargs):
        # TODO - add cache check and celery worker check
        return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")


# log / blog
class BlogList(ListView):
    model = models.Blog

    def get_queryset(self):
        return self.model.objects.filter(published=True)

    @method_decorator(beta_tester_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
