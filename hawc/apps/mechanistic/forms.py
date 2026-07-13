from crispy_forms import layout as cfl
from django import forms
from django.urls import reverse

from ..assessment.autocomplete import DSSToxAutocomplete
from ..common.autocomplete import (
    AutocompleteSelectWidget,
    AutocompleteTextWidget,
)

# from ..common.forms import ArrayCheckboxSelectMultiple, BaseFormHelper, QuillField
from ..common.forms import ArrayCheckboxSelectMultiple, BaseFormHelper, CopyForm, JSONListWidget

# from ..common.widgets import SelectMultipleOtherWidget, SelectOtherWidget
# from ..epi.autocomplete import CountryAutocomplete
from . import autocomplete, constants, models


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
        widgets = {
            "parameters_measured": ArrayCheckboxSelectMultiple(
                choices=constants.EndpointParameters.choices
            ),
        }

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


class TestDesignForm(forms.ModelForm):
    class Meta:
        model = models.TestDesign
        exclude = ("experiment",)
        widgets = {
            "concentrations_tested": JSONListWidget(
                prefix="concentrations_tested",
                row_fields=models.TestDesign.concentrations_tested_subfields,
            )
        }

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        prefix = f"testdesign-{kwargs.get('instance').pk if 'instance' in kwargs else 'new'}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if experiment:
            self.instance.experiment = experiment
        self.fields["test_system"].queryset = self.instance.experiment.testsystems.all()

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("vehicle", 2, "col-md-6")
        helper.add_row("final_concentration_vehicle", 2, "col-md-6")

        return helper


class MechControlForm(forms.ModelForm):
    class Meta:
        model = models.MechControl
        exclude = ("experiment",)
        widgets = {}

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        prefix = f"mechcontrol-{kwargs.get('instance').pk if 'instance' in kwargs else 'new'}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if experiment:
            self.instance.experiment = experiment
        # self.fields["test_system"].queryset = self.instance.experiment.testsystems.all()
        self.fields["test_system"].queryset = self.instance.experiment.testsystems.filter(
            controls_used=constants.ControlsUsed.YS
        )

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("test_system", 3, "col-md-4")

        return helper


class ExperimentalDesignForm(forms.ModelForm):
    class Meta:
        model = models.ExperimentalDesign
        exclude = ("experiment",)

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        prefix = (
            f"experimentaldesign-{kwargs.get('instance').pk if 'instance' in kwargs else 'new'}"
        )
        super().__init__(*args, prefix=prefix, **kwargs)
        if experiment:
            self.instance.experiment = experiment

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        # helper.add_row("vehicle", 2, "col-md-6")
        # helper.add_row("final_concentration_vehicle", 2, "col-md-6")

        return helper


class DataAnalysisForm(forms.ModelForm):
    class Meta:
        model = models.DataAnalysis
        exclude = ("experiment",)

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        prefix = f"dataanalysis-{kwargs.get('instance').pk if 'instance' in kwargs else 'new'}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if experiment:
            self.instance.experiment = experiment

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("validity", 2, "col-md-6")
        helper.add_row("cytotoxicity", 2, "col-md-6")
        helper.add_row("interference_tests", 2, "col-md-6")
        helper.add_row("detection_range", 2, "col-md-6")
        helper.add_row("data_calculation", 2, "col-md-6")
        helper.add_row("evaluation", 2, "col-md-6")

        return helper


class MechanisticEndpointForm(forms.ModelForm):
    class Meta:
        model = models.MechanisticEndpoint
        exclude = (
            "experiment",
            "assessment",
            "effects",
        )
        widgets = {
            "system_term": forms.HiddenInput,
            "name_term": forms.HiddenInput,
            "organ_term": forms.HiddenInput,
            "effect_term": forms.HiddenInput,
            "effect_subtype_term": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        prefix = f"endpoint-{kwargs.get('instance').pk if 'instance' in kwargs else 'new'}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if experiment:
            self.instance.experiment = experiment
            self.instance.assessment = experiment.get_assessment()

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False

        helper.layout.insert(
            helper.find_layout_idx_for_field_name("name"),
            cfl.Div(id="vocabWidgets"),
        )

        helper.add_row("poa_process", 2, "col-md-6")
        helper.add_row("poa_object", 2, "col-md-6")
        helper.add_row("poa_action", 2, "col-md-6")
        # helper.add_row("final_concentration_vehicle", 2, "col-md-6")

        return helper

    NAME_REQ = "Endpoint/Adverse outcome is required"

    def clean(self):
        cleaned_data = super().clean()

        """
        # see animalv2 clean method...
        errors = self.clean_endpoint(self.instance, cleaned_data)
        for key, value in errors.items():
            self.add_error(key, value)
        """

        # the name input is hidden and overridden, so any "name" field error
        # must be displayed instead as a non_field_error
        name_error = self.errors.get("name", None)
        if name_error is not None:
            self.add_error(None, self.NAME_REQ)

        return cleaned_data
