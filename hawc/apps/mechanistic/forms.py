from django import forms
from django.urls import reverse

from ..assessment.autocomplete import DSSToxAutocomplete
from ..common.autocomplete import (
    AutocompleteSelectWidget,
    AutocompleteTextWidget,
)

# from ..common.forms import ArrayCheckboxSelectMultiple, BaseFormHelper, QuillField
from ..common.forms import BaseFormHelper, CopyForm

# from ..common.widgets import SelectMultipleOtherWidget, SelectOtherWidget
# from ..epi.autocomplete import CountryAutocomplete
from . import autocomplete, models


class ExperimentForm(forms.ModelForm):
    CREATE_LEGEND = "Create new mechanistic experiment"
    CREATE_HELP_TEXT = ""
    UPDATE_HELP_TEXT = "Update an existing mechanistic experiment."

    class Meta:
        model = models.Experiment
        exclude = ("study",)
        # widgets = { }
        """
        field_classes = {
            "comments": QuillField,
        }
        """

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

        helper.add_row("guideline", 3, "col-md-4")
        # helper.add_row("age_profile", 4, "col-md-3")
        # helper.add_row("participant_n", 3, "col-md-4")
        # helper.add_row("countries", 2, "col-md-4")
        # helper.add_row("criteria", 3, "col-md-4")
        return helper


class ExperimentSelectorForm(CopyForm):
    legend_text = "Copy experiment"
    help_text = "Select an existing experiment as a template to create a new one."
    create_url_pattern = "mechanistic:experiment_create"
    selector = forms.ModelChoiceField(
        queryset=models.Experiment.objects.all(), empty_label=None, label="Select template"
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.fields["selector"].queryset = self.fields["selector"].queryset.filter(
            study=self.parent
        )


class ChemicalForm(forms.ModelForm):
    class Meta:
        model = models.Chemical
        # exclude = ("experiment",)
        exclude = ("study",)
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
        """
        experiment = kwargs.pop("parent", None)
        prefix = f"chemical-{kwargs.get('instance').pk if 'instance' in kwargs else 'new'}"
         super().__init__(*args, prefix=prefix, **kwargs)
        if experiment:
            self.instance.experiment = experiment
        """

        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study

    @property
    def helper(self):
        inputs = {
            "legend_text": ("Add" if not self.instance.id else "Update") + " Chemical",
            "cancel_url": self.instance.study.get_absolute_url(),
            "submit_text": "Save",
        }
        helper = BaseFormHelper(self, **inputs)
        # helper = BaseFormHelper(self)
        # helper.form_tag = False
        helper.form_id = "form-mech-chemical"
        helper.add_row("dsstox", 3, "col-md-4")
        helper.add_row("composition_purity", 2, "col-md-6")
        helper.add_create_btn("dsstox", reverse("assessment:dtxsid_create"), "Add new DTXSID")
        return helper


class ChemicalSelectorForm(CopyForm):
    legend_text = "Copy chemical"
    help_text = "Select an existing chemical as a template to create a new one."
    create_url_pattern = "mechanistic:chemical_create"
    selector = forms.ModelChoiceField(
        queryset=models.Chemical.objects.all(), empty_label=None, label="Select template"
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.fields["selector"].queryset = self.fields["selector"].queryset.filter(
            study=self.parent
        )


class TestSystemForm(forms.ModelForm):
    class Meta:
        model = models.TestSystem
        exclude = ("experiment",)
        widgets = {
            "name": AutocompleteTextWidget(
                autocomplete_class=autocomplete.TestSystemAutocomplete, field="name"
            ),
        }

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        prefix = f"testsystem-{kwargs.get('instance').pk if 'instance' in kwargs else 'new'}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if experiment:
            self.instance.experiment = experiment

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("test_system_type", 2, "col-md-6")
        helper.add_row("supplier", 2, "col-md-6")
        helper.add_row("genetic_modification", 2, "col-md-6")
        helper.add_row("metabolic_competence", 2, "col-md-6")
        helper.add_row("medium_buffer", 2, "col-md-6")
        helper.add_row("qc_confirmation", 2, "col-md-6")

        assessment_id = self.instance.experiment.study.assessment.pk
        helper.add_create_btn(
            "species", reverse("assessment:species_create", args=(assessment_id,)), "Create species"
        )

        return helper


class MethodForm(forms.ModelForm):
    class Meta:
        model = models.Method
        exclude = ("experiment",)
        # widgets = { }

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        prefix = f"method-{kwargs.get('instance').pk if 'instance' in kwargs else 'new'}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if experiment:
            self.instance.experiment = experiment
        self.fields["test_system"].queryset = self.instance.experiment.testsystems.all()

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        # helper.add_row("test_system_type", 2, "col-md-6")

        return helper
