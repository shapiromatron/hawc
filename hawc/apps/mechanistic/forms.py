from django import forms
from django.urls import reverse

from ..assessment.autocomplete import DSSToxAutocomplete
from ..common.autocomplete import (
    AutocompleteSelectWidget,
    AutocompleteTextWidget,
)
# from ..common.forms import ArrayCheckboxSelectMultiple, BaseFormHelper, QuillField
from ..common.forms import BaseFormHelper, QuillField
# from ..common.widgets import SelectMultipleOtherWidget, SelectOtherWidget
# from ..epi.autocomplete import CountryAutocomplete
from . import autocomplete, constants, models
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


class ChemicalForm(forms.ModelForm):
    class Meta:
        model = models.Chemical
        exclude = ("experiment",)
        widgets = {
            "name": AutocompleteTextWidget(
                autocomplete_class=autocomplete.ChemicalAutocomplete, field="name"
            ),
            "dsstox": AutocompleteSelectWidget(autocomplete_class=DSSToxAutocomplete),
            "cas": AutocompleteTextWidget(
                autocomplete_class=autocomplete.ChemicalAutocomplete, field="cas"
            ),
        }

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        prefix = f"chemical-{kwargs.get('instance').pk if 'instance' in kwargs else 'new'}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if experiment:
            self.instance.experiment = experiment

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("dsstox", 3, "col-md-4")
        # helper.add_row("summary", 4, "col-md-3")
        helper.add_create_btn("dsstox", reverse("assessment:dtxsid_create"), "Add new DTXSID")
        return helper
