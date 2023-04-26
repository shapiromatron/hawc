import plotly.express as px
from django.apps import apps
from django.middleware.csrf import get_token
from django.urls import reverse
from django.views.generic import ListView

from ..assessment.constants import AssessmentViewPermissions
from ..assessment.models import Assessment
from ..common.crumbs import Breadcrumb
from ..common.helper import WebappConfig
from ..common.views import BaseList, LoginRequiredMixin, WebappMixin
from ..myuser.models import HAWCUser
from ..study.serializers import StudyAssessmentSerializer
from . import constants, models


def mgmt_dashboard_breadcrumb(assessment) -> Breadcrumb:
    return Breadcrumb(
        name="Management dashboard", url=reverse("mgmt:assessment_dashboard", args=(assessment.id,))
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


# User-level task views
class RobTaskMixin:
    """
    Add risk of bias tasks for a user to task views.
    """

    def get_rob_queryset(self, RiskOfBias):
        raise NotImplementedError("Abstract method; requires implementation")

    def get_review_tasks(self):
        RiskOfBias = apps.get_model("riskofbias", "RiskOfBias")
        rob_tasks = self.get_rob_queryset(RiskOfBias)
        self._study_ids = rob_tasks.values_list("study_id", flat=True)
        filtered_tasks = [rob for rob in rob_tasks if rob.is_complete is False]
        return RiskOfBias.get_qs_json(filtered_tasks, json_encode=False)

    def get_review_studies(self):
        Study = apps.get_model("study", "Study")
        study_qs = Study.objects.filter(id__in=self._study_ids).select_related("assessment")
        study_ser = StudyAssessmentSerializer(study_qs, many=True)
        # must cast to list to circumvent error when included in pydantic model
        return list(study_ser.data)

    def get_app_config(self, context) -> WebappConfig:
        assessment_id = self.assessment.id if hasattr(self, "assessment") else None
        task_url = (
            reverse("mgmt:api:task-assessment-assignments")
            if assessment_id
            else reverse("mgmt:api:task-assignments")
        )
        return WebappConfig(
            app="mgmtStartup",
            page="TaskAssignments",
            data={
                "assessment_id": assessment_id,
                "csrf": get_token(self.request),
                "user": self.request.user.id,
                "rob_tasks": self.get_review_tasks(),
                "rob_studies": self.get_review_studies(),
                "tasks": {
                    "submit_url": reverse("mgmt:api:task-list"),
                    "url": task_url,
                    "list": self.model.get_qs_json(context["object_list"], json_encode=False),
                },
                "autocomplete": {"url": reverse("autocomplete", args=("myuser-userautocomplete",))},
            },
        )


class UserAssignments(RobTaskMixin, WebappMixin, LoginRequiredMixin, ListView):
    model = models.Task
    template_name = "mgmt/user_assignments.html"

    def get_queryset(self):
        return (
            self.model.objects.all()
            .owned_by(self.request.user)
            .order_by("-study__assessment_id", "study__short_citation", "type")
        )

    def get_rob_queryset(self, RiskOfBias):
        return RiskOfBias.objects.filter(author=self.request.user, active=True)

    def get_review_tasks2(self):
        RiskOfBias = apps.get_model("riskofbias", "RiskOfBias")
        rob_tasks = self.get_rob_queryset(RiskOfBias)
        self._study_ids = rob_tasks.values_list("study_id", flat=True)
        return [rob for rob in rob_tasks if rob.is_complete is False]

    def get_context_data(self, **kwargs):
        show_completed = self.request.GET.get("completed", "off") == "on"
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(self.request.user, "Assigned tasks")
        context["rob_task_list"] = self.get_review_tasks2()
        if not show_completed:
            context["object_list"] = context["object_list"].exclude(status__in=[30, 40])
        context["show_completed"] = show_completed
        return context


class UserAssessmentAssignments(RobTaskMixin, LoginRequiredMixin, BaseList):
    parent_model = Assessment
    model = models.Task
    template_name = "mgmt/user_assessment_assignments.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(study__assessment=self.assessment)
            .owned_by(self.request.user)
            .select_related("owner", "study", "study__reference_ptr", "study__assessment")
        )

    def get_incomplete_tasks(self):
        return self.model.objects.all().owned_by(self.request.user).exclude(status=30)

    def get_rob_queryset(self, RiskOfBias):
        return RiskOfBias.objects.filter(
            author=self.request.user, active=True, study__assessment=self.assessment
        )

    def get_review_tasks2(self):
        RiskOfBias = apps.get_model("riskofbias", "RiskOfBias")
        rob_tasks = self.get_rob_queryset(RiskOfBias)
        self._study_ids = rob_tasks.values_list("study_id", flat=True)
        return [rob for rob in rob_tasks if rob.is_complete is False]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, mgmt_dashboard_breadcrumb(self.assessment))
        context["breadcrumbs"][3] = Breadcrumb(name="My assigned tasks")
        context["rob_task_list"] = self.get_review_tasks2
        context["incomplete_task_list"] = self.get_incomplete_tasks()
        return context


def get_task_plot(qs, title=""):
    df = qs.values_list("status", flat=True)
    status_count = {name: 0 for name in constants.TaskStatus.labels}
    for status in df:
        status_count[constants.TaskStatus(status).label] += 1
    task_plot = px.bar(
        x=list(status_count.values()),
        y=list(status_count.keys()),
        orientation="h",
        title=title,
        width=500,
        height=200,
        template="none",
        color=list(status_count.keys()),
        color_discrete_sequence=["#cfcfcf", "#fecc01", "#02cc00", "#ff0000"],
        text_auto=True,
    )
    task_plot.update_layout(
        xaxis={"title": "Tasks"},
        yaxis={"title": "", "autorange": "reversed"},
        margin={"l": 85, "r": 0, "t": 30, "b": 30},
        showlegend=False,
        hovermode=False,
    )
    return task_plot


# Assessment-level task views
class TaskDashboard(BaseList):
    parent_model = Assessment
    model = models.Task
    template_name = "mgmt/assessment_dashboard.html"
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER

    def get_queryset(self):
        return super().get_queryset().filter(study__assessment_id=self.assessment.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][2] = Breadcrumb(name="Management dashboard")
        context["all_tasks_plot"] = get_task_plot(context["object_list"])
        context["type_plots"] = [
            get_task_plot(context["object_list"].filter(type=key), title=label)
            for key, label in constants.TaskType.choices
        ]
        user_list = set(context["object_list"].values_list("owner", flat=True))
        user_qs = HAWCUser.objects.filter(id__in=user_list)
        context["user_plots"] = [
            get_task_plot(context["object_list"].filter(owner=user), title=user.get_full_name())
            for user in user_qs
        ]
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="mgmtStartup", page="Dashboard", data=dict(assessment_id=self.assessment.id)
        )


class TaskDetail(TaskDashboard):
    template_name = "mgmt/assessment_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(2, mgmt_dashboard_breadcrumb(self.assessment))
        context["breadcrumbs"][3] = Breadcrumb(name="Assignments")
        return context

    def get_app_config(self, context) -> WebappConfig:
        a_id = self.assessment.id
        return WebappConfig(
            app="mgmtStartup",
            page="TaskTable",
            data=dict(
                assessment_id=a_id,
                csrf=get_token(self.request),
                tasksListUrl=reverse("mgmt:api:task-list") + f"?assessment_id={a_id}",
                taskUpdateBaseUrl=reverse("mgmt:api:task-list"),
                studyListUrl=reverse("study:api:study-list") + f"?assessment_id={a_id}",
                userAutocompleteUrl=reverse("autocomplete", args=("myuser-userautocomplete",)),
            ),
        )
