import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView

from ..assessment.models import Assessment
from ..common.crumbs import Breadcrumb
from ..common.views import (
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseList,
    BaseUpdate,
    BaseUpdateWithFormset,
    MessageMixin,
    ProjectManagerOrHigherMixin,
    TeamMemberOrHigherMixin,
    TimeSpentOnPageMixin,
    get_referrer,
)
from ..study.models import Study
from . import forms, models


def get_breadcrumb_rob_setting(assessment) -> Breadcrumb:
    return Breadcrumb(
        name=f"{assessment.get_rob_name_display()} requirements",
        url=reverse("riskofbias:arob_detail", args=(assessment.id,)),
    )


def get_breadcrumb_rob_reviews(assessment) -> Breadcrumb:
    return Breadcrumb(
        name=f"{assessment.get_rob_name_display()} assignments",
        url=reverse("riskofbias:arob_reviewers", args=(assessment.id,)),
    )


# Assessment risk of bias requirements
class ARoBDetail(BaseList):
    parent_model = Assessment
    model = models.RiskOfBiasDomain
    template_name = "riskofbias/arob_detail.html"

    def get_queryset(self):
        return self.model.objects.get_qs(self.assessment).prefetch_related("metrics")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][2] = get_breadcrumb_rob_setting(self.assessment)
        return context


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
        context["breadcrumbs"].append(get_breadcrumb_rob_setting(self.assessment))
        context["breadcrumbs"].append(Breadcrumb(name="Update"))
        context["config"] = json.dumps(
            {
                "assessment_id": self.assessment.id,
                "api_url": f"{reverse('riskofbias:api:domain-list')}?assessment_id={self.assessment.id}",
                "submit_url": f"{reverse('riskofbias:api:domain-order-rob')}?assessment_id={self.assessment.id}",
                "cancel_url": reverse("riskofbias:arob_detail", args=(self.assessment.id,)),
                "csrf": get_token(self.request),
            }
        )
        return context


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
            [get_breadcrumb_rob_setting(self.assessment), Breadcrumb(name="Copy")]
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["assessment"] = self.assessment
        return kwargs

    def form_valid(self, form):
        form.copy_riskofbias()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("riskofbias:arob_detail", kwargs={"pk": self.assessment.pk})


class ARoBReviewersList(TeamMemberOrHigherMixin, BaseList):
    """
    List an assessment's studies with their active risk of bias reviewers.
    """

    parent_model = Assessment
    model = Study
    template_name = "riskofbias/reviewers_list.html"

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.parent_model, pk=kwargs["pk"])

    def get_queryset(self):
        return self.model.objects.get_qs(self.assessment).prefetch_related(
            Prefetch(
                "riskofbiases",
                queryset=models.RiskOfBias.objects.all_active().prefetch_related(
                    "author", "scores",
                ),
                to_attr="active_riskofbiases",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rob_count"] = self.assessment.rob_settings.number_of_reviewers + 1
        context["breadcrumbs"].insert(2, get_breadcrumb_rob_setting(self.assessment))
        context["breadcrumbs"][3] = Breadcrumb(name="Reviewer assignment")
        return context


class ARoBReviewersUpdate(ProjectManagerOrHigherMixin, BaseUpdateWithFormset):
    """
    Creates the specified number of RiskOfBiases, one for each reviewer in the
    form. If the `number of reviewers` field is 1, then the only review is also
    the final review. If the `number of reviewers` field is more than one, then
    a final review is created in addition to the `number of reviewers`
    """

    model = Assessment
    form_class = forms.NumberOfReviewersForm
    formset_factory = forms.RoBReviewerFormset
    success_message = "Reviewers updated."
    template_name = "riskofbias/reviewers_form.html"

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.model, pk=kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, get_breadcrumb_rob_setting(self.assessment))
        context["breadcrumbs"].insert(3, get_breadcrumb_rob_reviews(self.assessment))
        context["breadcrumbs"][4] = Breadcrumb(name="Update")
        return context

    def build_initial_formset_factory(self):
        queryset = (
            Study.objects.get_qs(self.assessment)
            .prefetch_related("identifiers")
            .prefetch_related("searches")
            .prefetch_related("assessment__rob_settings")
            .prefetch_related(
                Prefetch(
                    "riskofbiases",
                    queryset=models.RiskOfBias.objects.active(),
                    to_attr="active_riskofbiases",
                )
            )
        )

        return self.formset_factory(queryset=queryset)

    def pre_validate(self, form, formset):
        # if number_of_reviewers changes, change required on fields
        if form.is_valid() and "number_of_reviewers" in form.changed_data:
            n = form.cleaned_data["number_of_reviewers"]
            required_fields = ["reference_ptr", "final_author"]
            if n == 1:
                n = 0
            [required_fields.append(f"author-{i}") for i in range(n)]
            for rob_form in formset.forms:
                for field in rob_form.fields:
                    if field not in required_fields:
                        rob_form.fields[field].required = False

    def post_object_save(self, form, formset):
        if "number_of_reviewers" in form.changed_data:
            n = form.cleaned_data["number_of_reviewers"]
            old_n = form.fields["number_of_reviewers"].initial
            n_diff = n - old_n
            # deactivate robs if number_of_reviewers is lowered.
            if n_diff < 0:
                if n == 1:
                    n = 0
                for rob_form in formset.forms:
                    deactivate_robs = rob_form.instance.get_active_robs(with_final=False)[n:]
                    for rob in deactivate_robs:
                        rob.deactivate()
            # if n_of_r is increased, activate inactive robs with most recent last_updated
            else:
                for rob_form in formset.forms:
                    activate_robs = rob_form.instance.riskofbiases.filter(
                        active=False, final=False
                    ).order_by("last_updated")[:n]
                    for rob in activate_robs:
                        rob.activate()

    def get_success_url(self):
        return reverse_lazy("riskofbias:arob_reviewers", args=(self.assessment.id,))


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].append(Breadcrumb(name=self.assessment.get_rob_name_display()))
        return context


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
        context["config"] = json.dumps(
            {
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
            }
        )
        context["breadcrumbs"].insert(2, get_breadcrumb_rob_reviews(self.assessment))
        context["breadcrumbs"][4] = Breadcrumb(name="Update review")
        return context
