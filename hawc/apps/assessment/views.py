import json
import logging
from typing import Any

from django.apps import apps
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.db.models import Count
from django.http import (
    Http404,
    HttpRequest,
    HttpResponseNotAllowed,
    HttpResponseRedirect,
    JsonResponse,
)
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, FormView, ListView, TemplateView, View
from django.views.generic.edit import CreateView

from ...services.utils.rasterize import get_styles_svg_definition
from ..common.crumbs import Breadcrumb
from ..common.helper import WebappConfig
from ..common.htmx import HtmxViewSet, action, can_edit, can_view
from ..common.views import (
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseList,
    BaseUpdate,
    CloseIfSuccessMixin,
    LoginRequiredMixin,
    MessageMixin,
    TimeSpentOnPageMixin,
    beta_tester_required,
    create_object_log,
    get_referrer,
)
from ..materialized.models import refresh_all_mvs
from . import constants, forms, models, serializers

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
            return constants.RobName.ROB.label
        elif settings.HAWC_FLAVOR == "EPA":
            return constants.RobName.SE.label
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
            back_href=get_referrer(self.request, reverse("portal")),
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


class Error401Response(TemplateResponse):
    status_code = 401  # Unauthorized


class Error401(TemplateView):
    response_class = Error401Response
    template_name = "401.html"


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
class AssessmentFullList(ListView):
    model = models.Assessment
    form_class = forms.AssessmentFilterForm
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()
        initial = self.request.GET if len(self.request.GET) > 0 else None  # bound vs unbound
        self.form = self.form_class(data=initial)
        return self.form.get_queryset(qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["breadcrumbs"] = Breadcrumb.build_crumbs(
                self.request.user, "Public assessments"
            )
        else:
            context["breadcrumbs"] = [Breadcrumb.build_root(self.request.user)]
        context["form"] = self.form
        return context


class AssessmentPublicList(ListView):
    model = models.Assessment
    form_class = forms.AssessmentFilterForm
    paginate_by = 50

    def get_queryset(self):
        qs = self.model.objects.get_public_assessments()
        initial = self.request.GET if len(self.request.GET) > 0 else None  # bound vs unbound
        self.form = self.form_class(data=initial)
        return self.form.get_queryset(qs)

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
        context["form"] = self.form
        context["is_public_list"] = True
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
        return super().get_success_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(self.request.user, "Create assessment")
        return context


class AssessmentRead(BaseDetail):
    model = models.Assessment

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "project_manager", "team_members", "reviewers", "datasets", "dtxsids", "values"
            )
        )

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
        context["values"] = self.object.values.order_by("value_type")
        context["adaf_footnote"] = constants.ADAF_FOOTNOTE
        return context


class AssessmentUpdate(BaseUpdate):
    success_message = "Assessment updated."
    model = models.Assessment
    form_class = forms.AssessmentForm
    assessment_permission = constants.AssessmentViewPermissions.PROJECT_MANAGER


class AssessmentModulesUpdate(AssessmentUpdate):
    success_message = "Assessment modules updated."
    form_class = forms.AssessmentModulesForm
    template_name = "assessment/assessment_module_form.html"
    assessment_permission = constants.AssessmentViewPermissions.PROJECT_MANAGER


class AssessmentDelete(BaseDelete):
    model = models.Assessment
    success_url = reverse_lazy("portal")
    success_message = "Assessment deleted."
    assessment_permission = constants.AssessmentViewPermissions.PROJECT_MANAGER


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

    def get_context_data(self, **kwargs):
        kwargs.update(EpiVersion=constants.EpiVersion)
        return super().get_context_data(**kwargs)


# Assessment Detail views
class AssessmentDetailCreate(BaseCreate):
    success_message = "Assessment Details created."
    model = models.AssessmentDetail
    parent_model = models.Assessment
    parent_template_name = "assessment"
    form_class = forms.AssessmentDetailForm

    def get_success_url(self):
        return self.object.assessment.get_absolute_url()


class AssessmentDetailUpdate(BaseUpdate):
    success_message = "Assessment Details updated."
    model = models.AssessmentDetail
    parent_model = models.Assessment
    form_class = forms.AssessmentDetailForm

    def get_success_url(self):
        return self.object.assessment.get_absolute_url()

    def get_cancel_url(self):
        return self.object.assessment.get_absolute_url()


# Assessment Value views
class AssessmentValueCreate(BaseCreate):
    success_message = "Assessment Value created."
    model = models.AssessmentValue
    parent_template_name = "assessment"
    parent_model = models.Assessment
    form_class = forms.AssessmentValueForm

    def get_success_url(self):
        return self.object.assessment.get_absolute_url()


class AssessmentValueUpdate(BaseUpdate):
    success_message = "Assessment Value updated."
    model = models.AssessmentValue
    parent_model = models.Assessment
    form_class = forms.AssessmentValueForm


class AssessmentValueDetail(BaseDetail):
    model = models.AssessmentValue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["adaf_footnote"] = constants.ADAF_FOOTNOTE
        return context


class AssessmentValueDelete(BaseDelete):
    model = models.AssessmentValue
    success_message = "Assessment Value deleted."

    def get_success_url(self):
        return self.object.assessment.get_absolute_url()


# Attachment viewset
class AttachmentViewset(HtmxViewSet):
    actions = {"create", "read", "update", "delete"}
    parent_model = models.Assessment
    model = models.Attachment
    form_fragment = "assessment/fragments/attachment_edit_row.html"
    detail_fragment = "assessment/fragments/attachment_row.html"
    list_fragment = "assessment/fragments/attachment_list.html"

    @action(permission=can_view, htmx_only=False)
    def read(self, request: HttpRequest, *args, **kwargs):
        if request.is_htmx:
            return render(request, self.detail_fragment, self.get_context_data())
        attachment = request.item.object
        if attachment.publicly_available or request.item.permissions(request.user)["edit"]:
            return HttpResponseRedirect(attachment.attachment.url)
        raise Http404()

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = forms.AttachmentForm(request.POST, request.FILES, parent=request.item.parent)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
        else:
            form = forms.AttachmentForm()
            template = self.list_fragment
        context = self.get_context_data(form=form)
        context["object_list"] = models.Attachment.objects.get_attachments(
            request.item.assessment, False
        )
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = forms.AttachmentForm(request.POST, request.FILES, instance=request.item.object)
            if form.is_valid():
                self.perform_update(request.item, form)
                template = self.detail_fragment
        else:
            form = forms.AttachmentForm(data=None, instance=request.item.object)
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            self.perform_delete(request.item)
            return self.str_response()
        return render(request, self.detail_fragment, self.get_context_data())


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


class CleanExtractedData(BaseEndpointList):
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
    assessment_permission = constants.AssessmentViewPermissions.TEAM_MEMBER

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
        response = {}
        if request.POST.get("refresh"):
            if request.user.is_authenticated:
                old_time = request.session.get_expiry_date().isoformat()
                request.session.set_expiry(None)  # use the global session expiry policy
                new_time = request.session.get_expiry_date().isoformat()
                response = {
                    "message": f"Session extended from {old_time} to {new_time}.",
                    "new_expiry_time": new_time,
                }
            else:
                response = {
                    "message": "Session not renewed.",
                    "new_expiry_time": None,
                }
        return JsonResponse(response)


@method_decorator(cache_page(60 * 60), name="dispatch")
class RasterizeCss(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"template": get_styles_svg_definition()})


class CleanStudyRoB(BaseDetail):
    template_name = "assessment/clean_study_rob_scores.html"
    model = models.Assessment
    breadcrumb_active_name = "Clean reviews"
    assessment_permission = constants.AssessmentViewPermissions.PROJECT_MANAGER

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

    def get_breadcrumbs(self) -> list[Breadcrumb]:
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

    def dispatch(self, request, *args, **kwargs):
        try:
            content_type = ContentType.objects.get_for_id(kwargs["content_type"])
        except ObjectDoesNotExist:
            raise Http404()
        first_log = self.model.objects.filter(**self.kwargs).first()
        if not first_log:
            first_log = self.model(content_type=content_type, object_id=kwargs["object_id"])
            if hasattr(first_log.content_object, "get_assessment"):
                first_log.assessment = first_log.content_object.get_assessment()
        if not first_log.user_can_view(request.user):
            raise PermissionDenied()

        self.first_log = first_log
        self.assessment = first_log.assessment

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.get_object_audit(**self.kwargs)

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        return Breadcrumb.build_crumbs(
            self.request.user,
            "Logs",
            [
                Breadcrumb.from_object(self.assessment),
                Breadcrumb(name="Logs", url=self.assessment.get_assessment_logs_url()),
            ],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(assessment=self.assessment, first_log=self.first_log)
        if self.assessment:
            context["breadcrumbs"] = self.get_breadcrumbs()
        return context


class AssessmentLogList(BaseList):
    parent_model = models.Assessment
    model = models.Log
    breadcrumb_active_name = "Logs"
    template_name = "assessment/assessment_log_list.html"
    paginate_by = 25
    assessment_permission = constants.AssessmentViewPermissions.TEAM_MEMBER

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .filter(assessment=self.assessment)
            .select_related("assessment", "content_type", "user")
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

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["content_types"] = self.get_cts()
        return context


class PublishedItemsChecklist(HtmxViewSet):
    actions = {"list", "update_item"}
    parent_actions = {"list", "update_item"}
    parent_model = models.Assessment
    model_lookups = {
        "study": apps.get_model("study", "Study"),
        "visual": apps.get_model("summary", "Visual"),
        "datapivot": apps.get_model("summary", "DataPivot"),
        "dataset": apps.get_model("assessment", "Dataset"),
        "summarytable": apps.get_model("summary", "SummaryTable"),
        "attachment": apps.get_model("assessment", "Attachment"),
    }

    @action(permission=can_edit, htmx_only=False)
    def list(self, request: HttpRequest, *args, **kwargs):
        return render(
            request,
            "assessment/published_items.html",
            self.get_list_context_data(self.request.user, self.request.item.assessment),
        )

    @action(permission=can_edit, methods={"post"})
    def update_item(self, request: HttpRequest, *args, **kwargs):
        instance = self.get_instance(request.item, kwargs["type"], kwargs["object_id"])
        self.perform_update(request, instance)
        return render(
            request,
            "assessment/fragments/publish_item_td.html",
            {"name": kwargs["type"], "object": instance, "assessment": request.item.assessment},
        )

    def get_instance(self, item, type: str, object_id: int):
        Model = self.model_lookups.get(type)
        if not Model:
            raise Http404()
        key = "object_id" if type == "attachment" else "assessment_id"
        return get_object_or_404(Model.objects.filter(**{key: item.assessment.id}), id=object_id)

    @transaction.atomic
    def perform_update(self, request, instance):
        if hasattr(instance, "published"):
            instance.published = not instance.published
        elif hasattr(instance, "publicly_available"):
            instance.publicly_available = not instance.publicly_available
        instance.save()
        create_object_log("Updated", instance, request.item.assessment.id, request.user.id)

    def get_list_context_data(self, user, assessment):
        crumbs = Breadcrumb.build_assessment_crumbs(user, assessment)
        crumbs.append(Breadcrumb(name="Published items"))
        studies = (
            apps.get_model("study", "Study")
            .objects.filter(assessment=assessment)
            .order_by("short_citation".lower())
        )
        datapivots = (
            apps.get_model("summary", "DataPivot")
            .objects.filter(assessment=assessment)
            .order_by("title".lower())
        )
        visuals = (
            apps.get_model("summary", "Visual")
            .objects.filter(assessment=assessment)
            .order_by("visual_type", "title".lower())
        )
        datasets = (
            apps.get_model("assessment", "Dataset")
            .objects.filter(assessment=assessment)
            .order_by("name".lower())
        )
        summarytables = (
            apps.get_model("summary", "SummaryTable")
            .objects.filter(assessment=assessment)
            .order_by("table_type", "title".lower())
        )
        attachments = apps.get_model("assessment", "Attachment").objects.get_attachments(
            assessment, False
        )
        return {
            "assessment": assessment,
            "breadcrumbs": crumbs,
            "studies": studies,
            "datapivots": datapivots,
            "visuals": visuals,
            "datasets": datasets,
            "summarytables": summarytables,
            "attachments": attachments,
        }
