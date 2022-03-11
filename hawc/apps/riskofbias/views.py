from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView

from ..assessment.models import Assessment
from ..common.crumbs import Breadcrumb
from ..common.helper import WebappConfig
from ..common.views import (
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseList,
    BaseUpdate,
    MessageMixin,
    ProjectManagerOrHigherMixin,
    TeamMemberOrHigherMixin,
    TimeSpentOnPageMixin,
    get_referrer,
)
from ..study.forms import StudyFilterForm
from ..study.models import Study
from . import forms, models


def get_breadcrumb_rob_setting(assessment, update: bool = False) -> Breadcrumb:
    if update:
        return Breadcrumb(
            name="Update", url=reverse("riskofbias:arob_update", args=(assessment.id,)),
        )
    else:
        return Breadcrumb(
            name=f"{assessment.get_rob_name_display()} requirements",
            url=reverse("riskofbias:arob_detail", args=(assessment.id,)),
        )


def get_breadcrumb_rob_reviews(assessment) -> Breadcrumb:
    return Breadcrumb(
        name=f"{assessment.get_rob_name_display()} assignments",
        url=reverse("riskofbias:rob_assignments", args=(assessment.id,)),
    )


# Assessment risk of bias requirements
class ARoBDetail(BaseList):
    parent_model = Assessment
    model = models.RiskOfBiasDomain
    template_name = "riskofbias/arob_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["no_data"] = models.RiskOfBiasDomain.objects.get_qs(self.assessment).count() == 0
        context["breadcrumbs"][2] = get_breadcrumb_rob_setting(self.assessment)
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="riskofbiasStartup",
            page="RobMetricsStartup",
            data=dict(
                assessment_id=self.assessment.id,
                api_url=f"{reverse('riskofbias:api:domain-list')}?assessment_id={self.assessment.id}",
                is_editing=False,
                csrf=get_token(self.request),
            ),
        )


class ARoBEdit(ProjectManagerOrHigherMixin, BaseDetail):
    """
    Displays a form for sorting and editing domain and metric.
    """

    crud = "Update"

    model = models.Assessment
    template_name = "riskofbias/arob_edit.html"

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.model, pk=kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["no_data"] = models.RiskOfBiasDomain.objects.get_qs(self.assessment).count() == 0
        context["breadcrumbs"].append(get_breadcrumb_rob_setting(self.assessment))
        context["breadcrumbs"].append(Breadcrumb(name="Update"))
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="riskofbiasStartup",
            page="RobMetricsStartup",
            data=dict(
                assessment_id=self.assessment.id,
                api_url=f"{reverse('riskofbias:api:domain-list')}?assessment_id={self.assessment.id}",
                submit_url=f"{reverse('riskofbias:api:domain-order-rob')}?assessment_id={self.assessment.id}",
                cancel_url=reverse("riskofbias:arob_detail", args=(self.assessment.id,)),
                is_editing=True,
                csrf=get_token(self.request),
            ),
        )


class ARoBTextEdit(ProjectManagerOrHigherMixin, BaseUpdate):
    parent_model = Assessment
    model = models.RiskOfBiasAssessment
    template_name = "riskofbias/arob_text_form.html"
    form_class = forms.RobTextForm
    success_message = "Help text has been updated."

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, assessment_id=self.assessment.pk)

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.parent_model, pk=kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][2] = get_breadcrumb_rob_setting(self.assessment)
        return context

    def get_success_url(self):
        return reverse_lazy("riskofbias:arob_detail", kwargs={"pk": self.assessment.pk})


class ARoBCopy(ProjectManagerOrHigherMixin, MessageMixin, FormView):
    model = models.RiskOfBiasDomain
    parent_model = Assessment
    template_name = "riskofbias/arob_copy.html"
    form_class = forms.RiskOfBiasCopyForm
    success_message = "Settings have been updated."

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.parent_model, pk=kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_assessment_crumbs(
            self.request.user, self.assessment
        )
        context["breadcrumbs"].extend(
            [
                get_breadcrumb_rob_setting(self.assessment),
                get_breadcrumb_rob_setting(self.assessment, update=True),
                Breadcrumb(name="Copy"),
            ]
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["assessment"] = self.assessment
        return kwargs

    def form_valid(self, form):
        form.evaluate()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("riskofbias:arob_update", args=(self.assessment.id,))


class ARoBLoadApproach(ARoBCopy):
    template_name = "riskofbias/arob_load_approach.html"
    form_class = forms.RiskOfBiasLoadApproachForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][-1].name = "Load approach"
        return context


def get_rob_assignment_data(assessment, studies):
    # custom data; the `robs` must match response in RiskOfBiasAssignmentSerializer
    return {
        "assessment_id": assessment.id,
        "number_of_reviewers": assessment.rob_settings.number_of_reviewers,
        "studies": [
            {
                "id": study.id,
                "short_citation": study.short_citation,
                "published": study.published,
                "url": study.get_absolute_url(),
                "robs": [
                    {
                        "id": rob.id,
                        "edit_url": rob.get_edit_url(),
                        "active": rob.active,
                        "is_complete": rob.is_complete,
                        "final": rob.final,
                        "author": rob.author_id,
                        "author_name": str(rob.author),
                        "study": rob.study_id,
                    }
                    for rob in study.robs
                ],
            }
            for study in studies
        ],
    }


class RobAssignmentList(TeamMemberOrHigherMixin, BaseList):
    parent_model = Assessment
    model = Study
    template_name = "riskofbias/rob_assignment_list.html"

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.parent_model, pk=kwargs["pk"])

    def get_queryset(self):
        robs = models.RiskOfBias.objects.filter(active=True).prefetch_related("author", "scores")
        qs = (
            super()
            .get_queryset()
            .filter(assessment=self.assessment)
            .prefetch_related(Prefetch("riskofbiases", queryset=robs, to_attr="robs"))
        )
        if not self.assessment.user_can_edit_object(self.request.user):
            raise PermissionDenied()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, get_breadcrumb_rob_setting(self.assessment))
        context["breadcrumbs"][3] = Breadcrumb(
            name=f"{self.assessment.get_rob_name_display()} assignments"
        )
        return context

    def get_app_config(self, context) -> WebappConfig:
        data = get_rob_assignment_data(assessment=self.assessment, studies=context["object_list"])
        data.update(
            edit=False,
            user_id=self.request.user.id,
            can_edit_assessment=context["obj_perms"]["edit_assessment"],
        )
        return WebappConfig(app="riskofbiasStartup", page="robAssignmentStartup", data=data)


class RobAssignmentUpdate(ProjectManagerOrHigherMixin, BaseList):
    parent_model = Assessment
    model = Study
    template_name = "riskofbias/rob_assignment_update.html"
    paginate_by = 25
    form_class = StudyFilterForm

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.parent_model, pk=kwargs["pk"])

    def get_queryset(self):
        robs = models.RiskOfBias.objects.prefetch_related("author", "scores")
        qs = (
            super()
            .get_queryset()
            .filter(assessment=self.assessment)
            .prefetch_related(Prefetch("riskofbiases", queryset=robs, to_attr="robs"))
        )
        can_edit = self.assessment.user_can_edit_assessment(self.request.user)
        if not can_edit:
            raise PermissionDenied()
        initial = self.request.GET if len(self.request.GET) > 0 else None  # bound vs unbound
        self.form = self.form_class(data=initial, can_edit=can_edit)
        if self.form.is_valid():
            qs = qs.filter(self.form.get_query())
        return qs

    def get_context_data(self, **kwargs):
        kwargs.update(form=self.form)
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, get_breadcrumb_rob_setting(self.assessment))
        context["breadcrumbs"].insert(3, get_breadcrumb_rob_reviews(self.assessment))
        context["breadcrumbs"][4] = Breadcrumb(name="Update")
        return context

    def get_app_config(self, context) -> WebappConfig:
        data = get_rob_assignment_data(assessment=self.assessment, studies=context["object_list"])
        data.update(
            edit=True,
            users=[
                {"id": user.id, "name": str(user)} for user in self.assessment.pms_and_team_users()
            ],
            csrf=get_token(self.request),
        )
        return WebappConfig(app="riskofbiasStartup", page="robAssignmentStartup", data=data)


class RobNumberReviewsUpdate(BaseUpdate):
    model = models.RiskOfBiasAssessment
    form_class = forms.NumberOfReviewersForm
    success_message = "Number of reviewers updated."
    template_name = "riskofbias/reviewers_form.html"

    def get_object(self, **kwargs):
        obj = get_object_or_404(self.model, assessment=self.kwargs.get("pk"),)
        obj = super().get_object(object=obj)
        if not self.assessment.user_can_edit_assessment(self.request.user):
            raise PermissionDenied()
        return obj

    def get_success_url(self):
        return reverse_lazy("riskofbias:rob_assignments_update", args=(self.assessment.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][2] = get_breadcrumb_rob_setting(self.assessment)
        context["breadcrumbs"].insert(3, get_breadcrumb_rob_reviews(self.assessment))
        return context


# Risk of bias domain views
class RoBDomainCreate(BaseCreate):
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.RiskOfBiasDomain
    form_class = forms.RoBDomainForm
    success_message = "Domain created."

    def get_success_url(self):
        return reverse_lazy("riskofbias:arob_update", kwargs={"pk": self.assessment.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, get_breadcrumb_rob_setting(self.assessment))
        return context


class RoBDomainUpdate(BaseUpdate):
    model = models.RiskOfBiasDomain
    form_class = forms.RoBDomainForm
    success_message = "Domain updated."

    def get_success_url(self):
        return reverse_lazy("riskofbias:arob_update", kwargs={"pk": self.assessment.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][2] = get_breadcrumb_rob_setting(self.assessment)
        return context


class RoBDomainDelete(BaseDelete):
    success_message = "Risk of bias domain deleted."
    model = models.RiskOfBiasDomain

    def get_success_url(self):
        return reverse_lazy("riskofbias:arob_update", kwargs={"pk": self.assessment.pk})

    def get_cancel_url(self) -> str:
        return reverse_lazy("riskofbias:arob_update", kwargs={"pk": self.assessment.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][2] = get_breadcrumb_rob_setting(self.assessment)
        return context


# Risk of bias metric views
class RoBMetricCreate(BaseCreate):
    parent_model = models.RiskOfBiasDomain
    parent_template_name = "domain"
    model = models.RiskOfBiasMetric
    form_class = forms.RoBMetricForm
    success_message = "Metric created."

    def get_success_url(self):
        return reverse_lazy("riskofbias:arob_update", kwargs={"pk": self.assessment.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][2] = get_breadcrumb_rob_setting(self.assessment)
        return context


class RoBMetricUpdate(BaseUpdate):
    model = models.RiskOfBiasMetric
    form_class = forms.RoBMetricForm
    success_message = "Metric updated."

    def get_success_url(self):
        return reverse_lazy("riskofbias:arob_update", kwargs={"pk": self.assessment.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][2] = get_breadcrumb_rob_setting(self.assessment)
        context["breadcrumbs"].pop(3)
        return context


class RoBMetricDelete(BaseDelete):
    success_message = "Metric deleted."
    model = models.RiskOfBiasMetric

    def get_success_url(self):
        return reverse_lazy("riskofbias:arob_update", kwargs={"pk": self.assessment.pk})

    def get_cancel_url(self) -> str:
        return reverse_lazy("riskofbias:arob_update", kwargs={"pk": self.assessment.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][2] = get_breadcrumb_rob_setting(self.assessment)
        context["breadcrumbs"].pop(3)
        return context


# RoB views
class RoBDetail(BaseDetail):
    """
    Detailed view of final risk of bias metric.
    """

    model = Study
    template_name = "riskofbias/rob_detail.html"

    def get_webapp_config(self, display: str) -> WebappConfig:
        return WebappConfig(
            app="riskofbiasStartup",
            page="TableStartup",
            data=dict(
                assessment_id=self.assessment.id,
                study=dict(id=self.object.study.id, url=reverse("study:api:study-list")),
                csrf=get_token(self.request),
                host=f"//{self.request.get_host()}",
                display=display,
                isForm=False,
            ),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].append(Breadcrumb(name=self.assessment.get_rob_name_display()))
        return context

    def get_app_config(self, context) -> WebappConfig:
        return self.get_webapp_config("final")


class RoBsDetailAll(TeamMemberOrHigherMixin, RoBDetail):
    """
    Detailed view of all active risk of bias metric, including final.
    """

    template_name = "riskofbias/rob_detail_all.html"

    def get_assessment(self, request, *args, **kwargs):
        self.object = get_object_or_404(Study, pk=kwargs["pk"])
        return self.object.get_assessment()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][3] = Breadcrumb(
            name=f"{self.assessment.get_rob_name_display()} (all reviews)"
        )
        return context

    def get_app_config(self, context) -> WebappConfig:
        return self.get_webapp_config("all")


class RoBEdit(TimeSpentOnPageMixin, BaseDetail):
    """
    Displays a form for editing the risk of bias metrics for the final review.
    Also displays the metrics for the other active risk of bias reviews.
    """

    model = models.RiskOfBias
    template_name = "riskofbias/rob_edit.html"

    def get_object(self, **kwargs):
        # either project managers OR the author can edit/view.
        obj = super().get_object(**kwargs)
        if obj.author != self.request.user and not self.assessment.user_can_edit_assessment(
            self.request.user
        ):
            raise PermissionDenied
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, get_breadcrumb_rob_reviews(self.assessment))
        context["breadcrumbs"][4] = Breadcrumb(name="Update review")
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="riskofbiasStartup",
            page="RobStudyFormStartup",
            data={
                "assessment_id": self.assessment.id,
                "cancelUrl": get_referrer(self.request, self.object.get_absolute_url()),
                "csrf": get_token(self.request),
                "host": f"//{self.request.get_host()}",
                "hawc_flavor": settings.HAWC_FLAVOR,
                "study": {
                    "id": self.object.study_id,
                    "api_url": reverse("study:api:study-detail", args=(self.object.study_id,)),
                    "url": reverse("study:api:study-list"),
                },
                "riskofbias": {
                    "id": self.object.id,
                    "url": reverse("riskofbias:api:review-list"),
                    "override_options_url": reverse(
                        "riskofbias:api:review-override-options", args=(self.object.id,)
                    ),
                    "scores_url": reverse("riskofbias:api:scores-list"),
                },
            },
        )
