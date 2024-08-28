from django import forms
from django.forms.widgets import DateInput

from ..common.forms import BaseFormHelper
from . import models


class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ("owner", "status", "due_date")
        widgets = {
            "due_date": DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        status_names = [
            (status.id, status.name)
            for status in models.TaskStatus.objects.filter(
                assessment=self.instance.study.assessment
            )
        ]
        self.fields["status"].widget = forms.Select(choices=status_names)
        self.fields["owner"].queryset = self.instance.study.assessment.pms_and_team_users()

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("owner", 3, "col-md-4")
        return helper
