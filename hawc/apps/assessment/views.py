import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from django.apps import apps
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count
from django.http import Http404, HttpResponseNotAllowed, HttpResponseRedirect, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import HttpResponse, get_object_or_404, render
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, FormView, ListView, TemplateView, View
from django.views.generic.edit import CreateView

from ..common.crumbs import Breadcrumb
from ..common.forms import DownloadPlotForm
from ..common.helper import WebappConfig
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
    get_referrer,
)
from ..materialized.models import refresh_all_mvs
from . import forms, models, serializers

logger = logging.getLogger(__name__)


def percentage(numerator, denominator):
    # Checking for denominator counts that are zero when dividing
    try:
        return numerator / float(denominator)
    except ZeroDivisionError:
        return 0


# General views
class Home(TemplateView):
    template_name = "hawc/home.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("portal"))
        if settings.EXTERNAL_HOME:
            return HttpResponseRedirect(settings.EXTERNAL_HOME)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_assessments"] = models.Assessment.objects.recent_public()
        context["page"] = models.Content.rendered_page(
            models.ContentTypeChoices.HOMEPAGE, self.request, context
        )
        return context


class About(TemplateView):
    template_name = "hawc/about.html"

    def dispatch(self, request, *args, **kwargs):
        if settings.EXTERNAL_ABOUT:
            return HttpResponseRedirect(settings.EXTERNAL_ABOUT)
        return super().dispatch(request, *args, **kwargs)

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
                apps.get_model("epi", "GroupResult")
                .objects.order_by("result_id")
                .distinct("result_id")
                .count()
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
            logger.info("Setting about-page cache")
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
        context.update(
            HAWC_FLAVOR=settings.HAWC_FLAVOR,
            rob_name=self.get_rob_name(),
            counts=self.get_object_counts(),
        )
        context["page"] = models.Content.rendered_page(
            models.ContentTypeChoices.ABOUT, self.request, context
        )
        return context


class Resources(TemplateView):
    template_name = "hawc/resources.html"

    def dispatch(self, request, *args, **kwargs):
        if settings.EXTERNAL_RESOURCES:
            return HttpResponseRedirect(settings.EXTERNAL_RESOURCES)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page"] = models.Content.rendered_page(
            models.ContentTypeChoices.RESOURCES, self.request, context
        )
        return context


class Contact(LoginRequiredMixin, MessageMixin, FormView):
    template_name = "hawc/contact.html"
    form_class = forms.ContactForm
    success_url = reverse_lazy("home")
    success_message = "Your message has been sent!"

    def dispatch(self, request, *args, **kwargs):
        if settings.EXTERNAL_CONTACT_US:
            return HttpResponseRedirect(settings.EXTERNAL_CONTACT_US)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            back_href=get_referrer(self.request, reverse("portal")), user=self.request.user,
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


class Error401Response(TemplateResponse):
    status_code = 401  # Unauthorized


class Error401(TemplateView):
    response_class = Error401Response
    template_name = "401.html"


@method_decorator(staff_member_required, name="dispatch")
class Swagger(TemplateView):
    template_name = "swagger.html"


# Assessment Object
class AssessmentList(LoginRequiredMixin, ListView):
    model = models.Assessment
    template_name = "assessment/assessment_home.html"

    def get(self, request, *args, **kwargs):
        if settings.ACCEPT_LICENSE_REQUIRED and not self.request.user.license_v2_accepted:
            return HttpResponseRedirect(reverse("user:accept-license"))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [Breadcrumb.build_root(self.request.user)]
        return context


@method_decorator(staff_member_required, name="dispatch")
class AssessmentFullList(LoginRequiredMixin, ListView):
    model = models.Assessment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["breadcrumbs"] = Breadcrumb.build_crumbs(
                self.request.user, "Public assessments"
            )
        else:
            context["breadcrumbs"] = [Breadcrumb.build_root(self.request.user)]
        return context


class AssessmentPublicList(ListView):
    model = models.Assessment

    def get_queryset(self):
        qs = self.model.objects.get_public_assessments()
        dtxsid = self.request.GET.get("dtxsid")
        if dtxsid:
            qs = qs.filter(dtxsids=dtxsid)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["breadcrumbs"] = Breadcrumb.build_crumbs(
                self.request.user, "Public assessments"
            )
        else:
            context["breadcrumbs"] = [Breadcrumb.build_root(self.request.user)]
        context[
            "desc"
        ] = """
            Publicly available assessments are below. Each assessment was conducted by an independent
            team; details on the objectives and methodology applied are described in each assessment.
            Data can also be downloaded for each individual assessment.
        """
        return context


class AssessmentCreate(TimeSpentOnPageMixin, UserPassesTestMixin, MessageMixin, CreateView):
    success_message = "Assessment created."
    model = models.Assessment
    form_class = forms.AssessmentForm
    template_name = "assessment/assessment_create_form.html"

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.can_create_assessments()

    def get_success_url(self):
        self.assessment = self.object
        response = super().get_success_url()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(self.request.user, "Create assessment")
        return context


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
        context["internal_communications"] = self.object.get_communications()
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
        url = get_referrer(self.request, assessment.get_absolute_url())

        if not assessment.user_is_team_member_or_higher(request.user):
            raise PermissionDenied()

        assessment.bust_cache()
        refresh_all_mvs(force=True)

        self.send_message()
        return HttpResponseRedirect(url)


class AssessmentDownloads(BaseDetail):
    """
    Download assessment-level Microsoft Excel reports
    """

    model = models.Assessment
    template_name = "assessment/assessment_downloads.html"
    breadcrumb_active_name = "Downloads"


# Attachment views
class AttachmentCreate(BaseCreate):
    success_message = "Attachment added."
    parent_model = models.Assessment
    parent_template_name = "parent"
    template_name = "assessment/components/attachment_edit_row.html"
    model = models.Attachment
    form_class = forms.AttachmentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["new_attach"] = True
        return context

    @transaction.atomic
    def form_valid(self, form):
        super().form_valid(form)
        context = self.get_context_data()
        context["object_list"] = models.Attachment.objects.get_attachments(
            self.assessment, not context["obj_perms"]["edit"]
        )
        context["canEdit"] = context["obj_perms"]["edit"]
        return render(self.request, "assessment/components/attachment_row.html", context)


class AttachmentRead(BaseDetail):
    model = models.Attachment

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "HX-Request" in request.headers:
            return render(
                request,
                "assessment/components/attachment_row.html",
                {"object": self.object, "canEdit": True},
            )
        if self.assessment.user_is_part_of_team(self.request.user):
            return HttpResponseRedirect(self.object.attachment.url)
        else:
            return PermissionDenied


class AttachmentList(BaseList):
    model = models.Attachment
    parent_model = models.Assessment
    parent_template_name = "parent"
    template_name = "assessment/_attachment_list.html"
    object_list = None
    form_class = forms.AttachmentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = models.Attachment.objects.get_attachments(
            self.assessment, not context["obj_perms"]["edit"]
        )
        context["canEdit"] = context["obj_perms"]["edit"]
        context["object"] = context["assessment"]
        context["form"] = self.form_class()
        return context

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = self.get_context_data()
        if request.GET.get("new", -1) == "True":
            context["new_attach"] = True
        return render(request, "assessment/_attachment_list.html", context)


class AttachmentUpdate(BaseUpdate):
    success_message = "Assessment updated."
    template_name = "assessment/components/attachment_edit_row.html"
    model = models.Attachment
    form_class = forms.AttachmentForm

    def get_success_url(self):
        return reverse("assessment:attachment_detail", args=[self.object.pk])


class AttachmentDelete(BaseDelete):
    success_message = "Attachment deleted."
    model = models.Attachment

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        redirect = super().delete(self, request, *args, **kwargs)
        redirect.status_code = 303
        return redirect

    def get_success_url(self):
        return reverse("assessment:attachment_list", args=[self.assessment.pk])


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
    breadcrumb_active_name = "Endpoints"

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

    breadcrumb_active_name = "Clean extracted data"
    template_name = "assessment/clean_extracted_data.html"

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.parent_model, pk=kwargs["pk"])

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="textCleanupStartup",
            data=dict(
                assessment_id=self.assessment.id,
                assessment=reverse(
                    "assessment:api:assessment-endpoints", args=(self.assessment.id,)
                ),
                csrf=get_token(self.request),
            ),
        )


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


@method_decorator(csrf_exempt, name="dispatch")
class DownloadPlot(FormView):
    form_class = DownloadPlotForm
    http_method_names = ["post"]

    def form_invalid(self, form: DownloadPlotForm):
        # intentionally don't provide helpful data
        return JsonResponse({"valid": False}, status=400)

    def form_valid(self, form: DownloadPlotForm):
        url = get_referrer(self.request, "/<unknown>/")
        return form.process(url)


class CleanStudyRoB(ProjectManagerOrHigherMixin, BaseDetail):
    template_name = "assessment/clean_study_rob_scores.html"
    model = models.Assessment
    breadcrumb_active_name = "Clean reviews"

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.model, pk=kwargs["pk"])

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="riskofbiasStartup",
            page="ScoreCleanupStartup",
            data=dict(
                assessment_id=self.assessment.id,
                assessment=reverse(
                    "assessment:api:assessment-endpoints", args=(self.assessment.id,)
                ),
                items=dict(
                    url=reverse("riskofbias:api:metric_scores-list"),
                    patchUrl=reverse("riskofbias:api:score-cleanup-list"),
                ),
                studyTypes=dict(url=reverse("study:api:study-types")),
                csrf=get_token(self.request),
                host=f"//{self.request.get_host()}",
            ),
        )


@method_decorator(staff_member_required, name="dispatch")
class AdminDashboard(TemplateView):
    template_name = "admin/dashboard.html"


@method_decorator(staff_member_required, name="dispatch")
class AdminAssessmentSize(TemplateView):
    template_name = "admin/assessment-size.html"


@method_decorator(staff_member_required, name="dispatch")
class AdminMediaPreview(TemplateView):
    template_name = "admin/media-preview.html"

    def get_context_data(self, **kwargs):
        """
        Suffix-specific values were obtained by querying media file extensions:

        ```bash
        find {settings.MEDIA_ROOT} -type f | grep -o ".[^.]\\+$" | sort | uniq -c
        ```
        """
        context = super().get_context_data(**kwargs)
        obj = self.request.GET.get("item", "")
        media = Path(settings.MEDIA_ROOT)
        context["has_object"] = False
        resolved = media / obj
        context["object_name"] = str(Path(obj))
        if obj and resolved.exists() and media in resolved.parents:
            root_uri = self.request.build_absolute_uri(location=settings.MEDIA_URL[:-1])
            uri = resolved.as_uri().replace(media.as_uri(), root_uri)
            context["has_object"] = True
            context["object_uri"] = uri
            context["suffix"] = resolved.suffix.lower()
            if context["suffix"] in [".csv", ".json", ".ris", ".txt"]:
                context["object_text"] = resolved.read_text()
            if context["suffix"] in [".xls", ".xlsx"]:
                df = pd.read_excel(str(resolved))
                context["object_html"] = df.to_html(index=False)
            if context["suffix"] in [".jpg", ".jpeg", ".png", ".tif", ".tiff"]:
                context["object_image"] = True
            if context["suffix"] in [".pdf"]:
                context["object_pdf"] = True

        return context


# blog
@method_decorator(beta_tester_required, name="dispatch")
class BlogList(ListView):
    model = models.Blog

    def get_queryset(self):
        return self.model.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(self.request.user, "Blog")
        return context


# log
class LogDetail(DetailView):
    template_name = "assessment/log_detail.html"
    model = models.Log

    def get_object(self):
        obj = super().get_object()
        if not obj.user_can_view(self.request.user):
            raise PermissionDenied()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assessment"] = self.object.assessment
        context["breadcrumbs"] = self.get_breadcrumbs()
        return context

    def get_breadcrumbs(self) -> List[Breadcrumb]:
        extras = []
        if assessment := self.object.assessment:
            extras.extend(
                [
                    Breadcrumb.from_object(assessment),
                    Breadcrumb(name="Logs", url=assessment.get_assessment_logs_url()),
                ]
            )
        crumbs = Breadcrumb.build_crumbs(self.request.user, "Log", extras)
        return crumbs


class LogObjectList(ListView):
    template_name = "assessment/log_object_list.html"
    model = models.Log
    paginate_by = 25

    def get_queryset(self):
        qs = self.model.objects.filter(**self.kwargs)
        if qs.count() == 0:
            raise Http404()
        self.first_log = qs[0]
        self.assessment = qs[0].assessment
        if not qs[0].user_can_view(self.request.user):
            raise PermissionDenied()
        return qs

    def get_breadcrumbs(self) -> List[Breadcrumb]:
        crumbs = Breadcrumb.build_crumbs(
            self.request.user,
            "Logs",
            [
                Breadcrumb.from_object(self.assessment),
                Breadcrumb(name="Logs", url=self.assessment.get_assessment_logs_url()),
            ],
        )
        return crumbs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["first_log"] = self.first_log
        context["assessment"] = self.assessment
        context["breadcrumbs"] = self.get_breadcrumbs()
        return context


class AssessmentLogList(TeamMemberOrHigherMixin, BaseList):
    parent_model = models.Assessment
    model = models.Log
    breadcrumb_active_name = "Logs"
    template_name = "assessment/assessment_log_list.html"
    paginate_by = 25

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(models.Assessment, pk=kwargs["pk"])

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(assessment=self.assessment).select_related(
            "assessment", "content_type", "user"
        )
        self.form = forms.LogFilterForm(self.request.GET, assessment=self.assessment)
        if self.form.is_valid():
            qs = qs.filter(self.form.filters())
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        return context


@method_decorator(cache_page(3600), name="dispatch")
class AboutContentTypes(TemplateView):
    template_name = "assessment/content_types.html"

    def get_cts(self):
        cts = {f"{ct.app_label}.{ct.model}": ct for ct in ContentType.objects.all()}
        return [
            cts["assessment.assessment"],
            cts["assessment.attachment"],
            cts["assessment.dataset"],
            cts["lit.search"],
            cts["lit.reference"],
            cts["study.study"],
            cts["study.attachment"],
            cts["riskofbias.riskofbiasdomain"],
            cts["riskofbias.riskofbiasmetric"],
            cts["riskofbias.riskofbias"],
            cts["animal.experiment"],
            cts["animal.animalgroup"],
            cts["animal.dosingregime"],
            cts["animal.endpoint"],
            cts["bmd.session"],
            cts["epi.studypopulation"],
            cts["epi.comparisonset"],
            cts["epi.exposure"],
            cts["epi.outcome"],
            cts["epi.result"],
            cts["epimeta.metaprotocol"],
            cts["epimeta.metaresult"],
            cts["summary.summarytable"],
            cts["summary.visual"],
            cts["summary.datapivot"],
            cts["summary.datapivotupload"],
            cts["summary.datapivotquery"],
        ]

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["content_types"] = self.get_cts()
        return context
