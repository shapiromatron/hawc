from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from assessment.models import Assessment
from utils.views import LoginRequiredMixin, TeamMemberOrHigherMixin

from . import models


class UserAssignments(LoginRequiredMixin, ListView):
    model = models.Task
    template_name = 'mgmt/user_assignments.html'

    def get_queryset(self):
        return self.model.objects.owned_by(self.request.user)


class TaskDashboard(TeamMemberOrHigherMixin, ListView):
    model = models.Task
    template_name = 'mgmt/assessment_dashboard.html'

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(Assessment, pk=kwargs['pk'])

    def get_queryset(self):
        return self.model.objects.assessment_qs(self.assessment.id)


class TaskDetail(TaskDashboard):
    template_name = 'mgmt/assessment_details.html'


class TaskModify(TaskDashboard):
    template_name = 'mgmt/assessment_modify.html'
