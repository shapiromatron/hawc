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
        prefix = f"task-{kwargs.get('instance').pk if 'instance' in kwargs else 'new'}"
        super().__init__(*args, prefix=prefix, **kwargs)
        self.fields["owner"].queryset = self.instance.study.assessment.pms_and_team_users()

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("owner", 3, "col-md-4")
        return helper
