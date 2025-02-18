from crispy_forms import layout as cfl
from django import forms
from django.forms.widgets import DateInput, TextInput
from django.urls import reverse

from hawc.apps.assessment.models import Assessment

from ..common.forms import BaseFormHelper
from . import constants, models
from .actions import clone_approach


class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ("owner", "status", "due_date")
        widgets = {
            "due_date": DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.update(prefix=f"task-{kwargs.get("instance").pk if "instance" in kwargs else "new"}")
        super().__init__(*args, **kwargs)
        self.fields["status"].queryset = models.TaskStatus.objects.filter(
            assessment_id=self.instance.study.assessment_id
        )
        self.fields["owner"].queryset = self.instance.study.assessment.pms_and_team_users()

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("owner", 3, "col-md-4")
        return helper


class TypeForm(forms.ModelForm):
    class Meta:
        model = models.TaskType
        fields = ("name", "order", "description")

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if assessment:
            self.instance.assessment = assessment

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 3, ["col-md-3", "col-md-3", "col-md-6"])
        helper.set_textarea_height(("description",), 3)

        return helper


class StatusForm(forms.ModelForm):
    class Meta:
        model = models.TaskStatus
        fields = ("name", "order", "color", "terminal_status", "description")
        widgets = {"color": TextInput(attrs={"type": "color"})}

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if assessment:
            self.instance.assessment = assessment
            self.instance.value = self.instance.order

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row(
            "name", 6, ["col-md-2", "col-md-2", "col-md-2", "col-md-2", "col-md-4", "col-md-0"]
        )
        helper.set_textarea_height(("description",), 3)

        return helper


class TriggerForm(forms.ModelForm):
    class Meta:
        model = models.TaskTrigger
        fields = ("task_type", "current_status", "next_status", "event")

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if assessment:
            self.instance.assessment = assessment
        status_names = [
            (status.id, status.name)
            for status in models.TaskStatus.objects.filter(assessment=self.instance.assessment)
        ]
        type_names = [
            (type.id, type.name)
            for type in models.TaskType.objects.filter(assessment=self.instance.assessment)
        ]
        self.fields["task_type"].widget = forms.Select(choices=type_names)
        self.fields["current_status"].widget = forms.Select(choices=status_names)
        self.fields["next_status"].widget = forms.Select(choices=status_names)
        self.fields["event"].widget = forms.Select(choices=constants.StartTaskTriggerEvent)

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("task_type", 4, ["col-md-3", "col-md-3", "col-md-3", "col-md-3"])
        return helper


class TaskSetupCopyForm(forms.Form):
    assessment = forms.ModelChoiceField(
        label="Select an assessment", queryset=Assessment.objects.all(), empty_label=None
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance")
        self.user = kwargs.pop("user")
        self.assessment = kwargs.pop("assessment")
        super().__init__(*args, **kwargs)
        self.fields["assessment"].widget.attrs["class"] = "col-md-12"
        self.fields["assessment"].queryset = Assessment.objects.filter(
            enable_project_management=True
        ).user_can_view(self.user, exclusion_id=self.assessment.id)

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            legend_text="Copy task managment approach from another assessment",
            help_text="Copy task types, statuses, and triggers from an existing HAWC assessment which you have access to.",
            cancel_url=reverse("mgmt:task-setup-list", args=(self.assessment.id,)),
            submit_text="Copy from assessment",
        )
        helper.layout.insert(3, cfl.Div(css_id="approach"))
        helper.layout.insert(2, cfl.Div(css_id="extra_content_insertion"))
        return helper

    def evaluate(self):
        clone_approach(self.assessment, self.cleaned_data["assessment"], self.user.id)
