from django import forms

from hawc.apps.common.forms import BaseFormHelper

from . import models


class DesignForm(forms.ModelForm):
    CREATE_LEGEND = "Create new study-population"

    CREATE_HELP_TEXT = ""

    UPDATE_HELP_TEXT = "Update an existing study-population."

    class Meta:
        model = models.Design
        exclude = ("study",)
        labels = {}

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) == forms.Textarea:
                widget.attrs["rows"] = 3

        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": self.UPDATE_HELP_TEXT,
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": self.CREATE_LEGEND,
                "help_text": self.CREATE_HELP_TEXT,
                "cancel_url": self.instance.study.get_absolute_url(),
            }

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("study_design", 3, "col-md-4")
        helper.add_row("age_description", 3, "col-md-4")
        helper.add_row("summary", 2, "col-md-6")
        helper.add_row("countries", 4, "col-md-3")
        return helper


class ChemicalForm(forms.ModelForm):
    class Meta:
        model = models.Chemical
        exclude = ("design",)
        labels = {}

        def __init__(self, *args, **kwargs):
            design = kwargs.pop("parent", None)
            super().__init__(*args, **kwargs)
            if design:
                self.instance.design = design

        @property
        def helper(self):
            for fld in list(self.fields.keys()):
                widget = self.fields[fld].widget
                if type(widget) == forms.Textarea:
                    widget.attrs["rows"] = 3
            helper = BaseFormHelper(self)
            helper.form_tag = False
            helper.add_row("name", 2, "col-md-3")
            return helper


class ExposureForm(forms.ModelForm):
    class Meta:
        model = models.Exposure
        exclude = ("design",)
        labels = {}

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) == forms.Textarea:
                widget.attrs["rows"] = 3
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 3, "col-md-3")
        helper.add_row("measurement_timing", 4, "col-md-3")
        return helper


class OutcomeForm(forms.ModelForm):
    class Meta:
        model = models.Outcome
        exclude = ("design",)
        labels = {}

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) == forms.Textarea:
                widget.attrs["rows"] = 3
        helper = BaseFormHelper(self)
        helper.add_row("name", 3, "col-md-4")
        helper.form_tag = False
        return helper
