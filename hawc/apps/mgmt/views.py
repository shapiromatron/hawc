from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView

from ..assessment.constants import AssessmentViewPermissions
from ..assessment.models import Assessment
from ..common.crumbs import Breadcrumb
from ..common.helper import WebappConfig, cacheable
from ..common.htmx import HtmxGetMixin, HtmxViewSet, action, can_edit
from ..common.views import BaseDetail, BaseFilterList, BaseList, LoginRequiredMixin
from ..myuser.models import HAWCUser
from ..riskofbias.models import RiskOfBias
from ..study.models import Study
from . import constants, filterset, forms, models
from .analytics import overview, time_series, time_spent


def mgmt_dashboard_breadcrumb(assessment) -> Breadcrumb:
    return Breadcrumb(
        name="Management dashboard", url=reverse("mgmt:task-dashboard", args=(assessment.id,))
    )


def incomplete_rob_reviews(user, assessment: Assessment | None) -> list[RiskOfBias]:
    """Return RiskOfBias objects that have an incomplete RiskOfBias review by the current user."""
    qs = RiskOfBias.objects.all()
    if assessment:
        qs = qs.filter(study__assessment=assessment)
    qs = (
        qs.filter(active=True, author_id=user.id)
        .prefetch_related("scores")
        .select_related("study__assessment")
        .order_by("study__assessment_id", "study__short_citation")
    )
    return [rob for rob in qs if not rob.is_complete]


# View mixins for ensuring tasks are started
class EnsurePreparationStartedMixin:
    """Ensure the preparation task has been started if form is valid."""

    def get_success_url(self):
        models.Task.objects.ensure_preparation_started(self.object, self.request.user)
        return super().get_success_url()


class EnsureExtractionStartedMixin:
    """Ensure the extraction task has been started if form is valid."""

    def get_success_url(self):
        study = self.object.study
        user = self.request.user
        models.Task.objects.ensure_preparation_stopped(study)
        models.Task.objects.ensure_extraction_started(study, user)
        return super().get_success_url()


class UserTaskList(LoginRequiredMixin, ListView):
    model = models.Task
    template_name = "mgmt/user_task_list.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .owned_by(self.request.user)
            .filter(status__in=[10, 20])
            .order_by("-study__assessment_id", "id")
            .select_related("study__assessment")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = list(context["object_list"])
        reviews = incomplete_rob_reviews(self.request.user, assessment=None)
        assessments = {task.study.assessment for task in tasks}
        assessments.update({rob.study.assessment for rob in reviews})
        context["assessments"] = [
            {
                "assessment": assess,
                "num_tasks": len(list(filter(lambda d: d.study.assessment_id == assess.id, tasks))),
                "num_robs": len(
                    list(filter(lambda d: d.study.assessment_id == assess.id, reviews))
                ),
            }
            for assess in sorted(assessments, key=lambda d: (d.year, d.id), reverse=True)
        ]
        return context


class AssessmentTaskDashboard(BaseList):
    parent_model = Assessment
    model = models.Task
    template_name = "mgmt/assessment_dashboard.html"
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(study__assessment_id=self.assessment.id)
            .select_related("owner")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][2] = Breadcrumb(name="Management dashboard")
        user_qs = HAWCUser.objects.filter(
            id__in=context["object_list"].values_list("owner", flat=True).distinct()
        ).order_by("last_name", "id")
        qs = list(context["object_list"])
        context["all_tasks_plot"] = models.Task.barchart(qs)
        context["type_plots"] = [
            models.Task.barchart(filter(lambda el: el.type == key, qs), title=label)
            for key, label in constants.TaskType.choices
        ]
        context["user_plots"] = [
            models.Task.barchart(
                filter(lambda el: el.owner and el.owner.id == user.id, qs),
                title=user.get_full_name(),
            )
            for user in user_qs
        ]
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="mgmtStartup", page="Dashboard", data=dict(assessment_id=self.assessment.id)
        )


class AssessmentTaskList(BaseFilterList):
    parent_model = Assessment
    model = models.Task
    filterset_class = filterset.TaskFilterSet
    template_name = "mgmt/assessment_details.html"
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER
    paginate_by = 100

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(study__assessment_id=self.assessment.id)
            .select_related("study", "owner")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, mgmt_dashboard_breadcrumb(self.assessment))
        context["breadcrumbs"][3] = Breadcrumb(name="Assignments")
        return context


class AssessmentAnalytics(HtmxGetMixin, BaseDetail):
    model = Assessment
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER
    actions: set[str] = {"index", "time_series", "time_spent", "overview"}

    def index(self, request: HttpRequest, context: dict):
        context["breadcrumbs"].append(mgmt_dashboard_breadcrumb(self.assessment))
        context["breadcrumbs"].append(Breadcrumb(name="Analytics"))
        return render(request, "mgmt/analytics.html", context)

    def time_series(self, request: HttpRequest, context: dict):
        context = cacheable(
            lambda: time_series.get_context_data(self.assessment),
            f"mgmt:analytics:time_series:{self.assessment.id}",
        )
        return render(request, "mgmt/analytics/time_series.html", context)

    def time_spent(self, request: HttpRequest, context: dict):
        context = cacheable(
            lambda: time_spent.get_context_data(self.assessment),
            f"mgmt:analytics:time_spent:{self.assessment.id}",
        )
        return render(request, "mgmt/analytics/time_spent.html", context)

    def overview(self, request: HttpRequest, context: dict):
        context = cacheable(
            lambda: overview.get_context_data(self.assessment),
            f"mgmt:analytics:overview:{self.assessment.id}",
        )
        return render(request, "mgmt/analytics/overview.html", context)


class TaskViewSet(HtmxViewSet):
    actions = {"read", "update"}
    parent_model = Study
    model = models.Task
    form_fragment = "mgmt/fragments/task_form.html"
    detail_fragment = "mgmt/fragments/task_detail.html"

    @action(permission=can_edit)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = forms.TaskForm(data=data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)
