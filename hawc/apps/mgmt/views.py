from django.db.models import Prefetch, QuerySet
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView

from ..assessment.constants import AssessmentViewPermissions
from ..assessment.models import Assessment
from ..common.crumbs import Breadcrumb
from ..common.helper import WebappConfig
from ..common.htmx import HtmxGetMixin, HtmxViewSet, action, can_edit
from ..common.views import BaseDetail, BaseFilterList, BaseList, FilterSetMixin, LoginRequiredMixin
from ..myuser.models import HAWCUser
from ..riskofbias.models import RiskOfBias
from ..study.models import Study
from . import constants, filterset, forms, models
from .analytics.growth import get_context_data


def mgmt_dashboard_breadcrumb(assessment) -> Breadcrumb:
    return Breadcrumb(
        name="Management dashboard", url=reverse("mgmt:task-dashboard", args=(assessment.id,))
    )


def studies_with_active_user_reviews(user, task_qs: QuerySet[models.Task]) -> QuerySet[Study]:
    """Given a list of tasks, return studies that have an incomplete RiskOfBias
    review by the current user. Reviews may be complete or incomplete; we just
    check by the status of the mgmt.Task.
    """
    active_rob_tasks = task_qs.exclude_completed_and_abandonded().filter(
        type=constants.TaskType.ROB
    )
    own_reviews = RiskOfBias.objects.filter(author=user, active=True)
    return (
        Study.objects.filter(id__in=active_rob_tasks.values_list("study_id", flat=True))
        .prefetch_related(Prefetch("riskofbiases", own_reviews, to_attr="own_reviews"))
        .select_related("assessment")
    )


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


class UserTaskList(LoginRequiredMixin, FilterSetMixin, ListView):
    filterset_class = filterset.UserTaskFilterSet
    model = models.Task
    template_name = "mgmt/user_task_list.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .owned_by(self.request.user)
            .select_related("study__assessment")
            .order_by("-study__assessment_id", "study__short_citation", "type")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(self.request.user, "Assigned tasks")
        context["studies"] = {
            study.id: study
            for study in studies_with_active_user_reviews(
                self.request.user, self.object_list.filter(type=constants.TaskType.ROB)
            )
        }
        context["TaskType"] = constants.TaskType
        return context


class UserAssessmentTaskList(BaseFilterList):
    filterset_class = filterset.UserTaskFilterSet
    model = models.Task
    parent_model = Assessment
    template_name = "mgmt/user_assessment_task_list.html"
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .owned_by(self.request.user)
            .select_related("study__assessment")
            .filter(study__assessment=self.assessment)
            .order_by("study__short_citation", "type")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, mgmt_dashboard_breadcrumb(self.assessment))
        context["breadcrumbs"][3] = Breadcrumb(name="My assigned tasks")
        context["studies"] = {
            study.id: study
            for study in studies_with_active_user_reviews(
                self.request.user, self.object_list.filter(type=constants.TaskType.ROB)
            )
        }
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
    actions: set[str] = {"index", "time_series", "time_spent", "growth"}

    def index(self, request: HttpRequest, context: dict):
        return render(request, "mgmt/analytics.html", context)

    def time_series(self, request: HttpRequest, context: dict):
        return render(request, "mgmt/analytics/time_series.html", context)

    def time_spent(self, request: HttpRequest, context: dict):
        return render(request, "mgmt/analytics/time_spent.html", context)

    def growth(self, request: HttpRequest, context: dict):
        context = get_context_data(self)
        return render(request, "mgmt/analytics/growth.html", context)


class TaskViewSet(HtmxViewSet):
    actions = {"read", "update"}
    parent_model = Study
    model = models.Task
    form_fragment = "mgmt/fragments/task_form.html"
    detail_fragment = "mgmt/fragments/task_cell.html"

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
