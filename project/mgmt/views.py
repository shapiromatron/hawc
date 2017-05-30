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
class UserAssignments(LoginRequiredMixin, ListView):
    model = models.Task
    template_name = 'mgmt/user_assignments.html'

    def get_queryset(self):
        return self.model.objects.owned_by(self.request.user)


class UserAssessmentAssignments(LoginRequiredMixin, BaseList):
    parent_model = Assessment
    model = models.Task
    template_name = 'mgmt/user_assessment_assignments.html'


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
