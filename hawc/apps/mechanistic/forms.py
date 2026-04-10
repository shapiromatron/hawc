from django import forms

# from ..assessment.autocomplete import DSSToxAutocomplete
# from ..common.autocomplete import (
    # AutocompleteSelectMultipleWidget,
    # AutocompleteSelectWidget,
    # AutocompleteTextWidget,
# )
# from ..common.forms import ArrayCheckboxSelectMultiple, BaseFormHelper, QuillField
from ..common.forms import BaseFormHelper, QuillField
# from ..common.widgets import SelectMultipleOtherWidget, SelectOtherWidget
# from ..epi.autocomplete import CountryAutocomplete
# from . import autocomplete, constants, models
from . import models


class ExperimentForm(forms.ModelForm):
    CREATE_LEGEND = "Create new mechanistic experiment"
    CREATE_HELP_TEXT = ""
    UPDATE_HELP_TEXT = "Update an existing mechanistic experiment."

    class Meta:
        model = models.Experiment
        exclude = ("study",)
        # widgets = { }
        field_classes = {
            "comments": QuillField,
        }

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study

    @property
    def helper(self):
        if self.instance.id:
            helper = BaseFormHelper(self)
            helper.form_tag = False

        else:
            inputs = {
                "legend_text": self.CREATE_LEGEND,
                "help_text": self.CREATE_HELP_TEXT,
                "cancel_url": self.instance.study.get_absolute_url(),
                "submit_text": "Next",
            }
            helper = BaseFormHelper(self, **inputs)

        # helper.add_row("summary", 4, "col-md-3")
        # helper.add_row("age_profile", 4, "col-md-3")
        # helper.add_row("participant_n", 3, "col-md-4")
        # helper.add_row("countries", 2, "col-md-4")
        # helper.add_row("criteria", 3, "col-md-4")
        return helper

