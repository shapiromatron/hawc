from django.apps import apps
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from assessment.models import Assessment
from utils.views import BaseList, LoginRequiredMixin, TeamMemberOrHigherMixin

from . import models


# View mixins for ensuring tasks are started
class EnsurePreparationStartedMixin(object):
    """Ensure the preparation task has been started if form is valid."""

    def get_success_url(self):
        models.Task.objects.ensure_preparation_started(
            self.object,
            self.request.user
        )
        return super().get_success_url()


class EnsureExtractionStartedMixin(object):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_json'] = self.model.get_qs_json(context['object_list'], json_encode=True)
        context['review_tasks'] = self.get_review_tasks()
        return context

    def get_review_tasks(self):
        RiskOfBias = apps.get_model('riskofbias', 'RiskOfBias')
        rob_tasks = self.get_rob_queryset(RiskOfBias)
        filtered_tasks = [rob for rob in rob_tasks if rob.is_complete is False]
        return RiskOfBias.get_qs_json(filtered_tasks, json_encode=True)

    def get_rob_queryset(self, RiskOfBias):
        raise NotImplementedError('Abstract method; requires implementation')


class UserAssignments(RobTaskMixin, LoginRequiredMixin, ListView):
    model = models.Task
    template_name = 'mgmt/user_assignments.html'

    def get_queryset(self):
        return self.model.objects.owned_by(self.request.user)

    def get_rob_queryset(self, RiskOfBias):
        return RiskOfBias.objects\
            .filter(author=self.request.user, active=True)


class UserAssessmentAssignments(RobTaskMixin, LoginRequiredMixin, BaseList):
    parent_model = Assessment
    model = models.Task
    template_name = 'mgmt/user_assessment_assignments.html'

    def get_queryset(self):
        return self.model.objects.owned_by(self.request.user)\
            .filter(study__assessment=self.assessment)\
            .select_related('owner', 'study', 'study__reference_ptr', 'study__assessment')

    def get_rob_queryset(self, RiskOfBias):
        return RiskOfBias.objects\
            .filter(author=self.request.user, active=True,
                    study__assessment=self.assessment)


# Assessment-level task views
class TaskDashboard(TeamMemberOrHigherMixin, BaseList):
    parent_model = Assessment
    model = models.Task
    template_name = 'mgmt/assessment_dashboard.html'

    def get_assessment(self, *args, **kwargs):
        return get_object_or_404(Assessment, pk=kwargs['pk'])

    def get_queryset(self):
        return self.model.objects.assessment_qs(self.assessment.id)


class TaskDetail(TaskDashboard):
    template_name = 'mgmt/assessment_details.html'


class TaskModify(TaskDashboard):
    template_name = 'mgmt/assessment_modify.html'
