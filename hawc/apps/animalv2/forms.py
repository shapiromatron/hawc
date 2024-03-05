from django import forms
from django.forms import ModelForm
from django.urls import reverse

from ..assessment.autocomplete import DSSToxAutocomplete
from ..common.autocomplete import (
    AutocompleteSelectWidget,
    AutocompleteTextWidget,
)
from ..common.forms import BaseFormHelper, QuillField
from . import autocomplete, constants, models


class ExperimentForm(ModelForm):
    class Meta:
        model = models.Experiment
        exclude = ("study",)
        field_classes = {"comments": QuillField}

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if parent:
            self.instance.study = parent

        # change checkbox to select box
        self.fields["has_multiple_generations"].widget = forms.Select(
            choices=((True, "Yes"), (False, "No"))
        )

    @property
    def helper(self):
        # by default take-up the whole row
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs["class"] = "form-control"

        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": "Update an existing experiment.",
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new experiment",
                "help_text": """
                    Create a new experiment. Each experiment is a associated with a
                    study, and may have one or more collections of animals. For
                    example, one experiment may be a 2-year cancer bioassay,
                    while another multi-generational study. It is possible to
                    create multiple separate experiments within a single study,
                    with different study-designs, durations, or test-species.""",
                "cancel_url": self.instance.study.get_absolute_url(),
            }

        helper = BaseFormHelper(self, **inputs)

        helper.add_row("name", 3, "col-md-4")
        helper.form_id = "experiment-v2-form"
        return helper


class ChemicalForm(forms.ModelForm):
    class Meta:
        model = models.Chemical
        exclude = ("experiment",)
        widgets = {
            "name": AutocompleteTextWidget(
                autocomplete_class=autocomplete.ChemicalAutocomplete, field="name"
            ),
            "dtxsid": AutocompleteSelectWidget(autocomplete_class=DSSToxAutocomplete),
        }

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if experiment:
            self.instance.experiment = experiment

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 3, "col-md-4")
        helper.add_create_btn("dtxsid", reverse("assessment:dtxsid_create"), "Add new DTXSID")
        return helper


class AnimalGroupForm(forms.ModelForm):
    class Meta:
        model = models.AnimalGroup
        exclude = ("experiment",)

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if experiment:
            self.instance.experiment = experiment

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("species", 3, "col-md-4")
        helper.add_row("lifestage_at_exposure", 2, "col-md-6")
        helper.add_row("generation", 2, "col-md-6")

        assessment_id = self.instance.experiment.study.assessment.pk
        helper.add_create_btn(
            "species",
            reverse("assessment:species_create", args=(assessment_id,)),
            "Create species",
        )
        helper.add_create_btn(
            "strain",
            reverse("assessment:strain_create", args=(assessment_id,)),
            "Create strain",
        )
        return helper


class TreatmentForm(forms.ModelForm):
    class Meta:
        model = models.Treatment
        exclude = ("experiment",)

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if experiment:
            self.instance.experiment = experiment
        self.fields["chemical"].queryset = self.instance.experiment.v2_chemicals.all()

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("exposure_duration", 3, "col-md-4")

        return helper


class DoseGroupForm(forms.ModelForm):
    formset_parent_key = "treatment_id"

    class Meta:
        model = models.DoseGroup
        exclude = ("treatment",)

    def __init__(self, *args, **kwargs):
        treatment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if treatment:
            self.instance.treatment = treatment


# thx https://stackoverflow.com/questions/21754918/rendering-tabular-rows-with-formset-in-django-crispy-forms and https://stackoverflow.com/questions/42615357/cannot-pass-helper-to-django-crispy-formset-in-template
class DoseGroupFormHelper(BaseFormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.template = "bootstrap4/table_inline_formset.html"


class EndpointForm(forms.ModelForm):
    class Meta:
        model = models.Endpoint
        # TODO - for now, we've got EHV fields for controlled vocab in the model, but we'll hide them from UI
        exclude = (
            "experiment",
            "name_term",
            "system_term",
            "organ_term",
            "effect_term",
            "effect_subtype_term",
        )

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if experiment:
            self.instance.experiment = experiment
        # TODO - if/when we add EHV terms back in, we'll need this kind of filtering...
        # self.fields["name_term"].queryset = Term.objects.filter(type=VocabularyTermType.endpoint_name)
        # self.fields["system_term"].queryset = Term.objects.filter(type=VocabularyTermType.system)
        # self.fields["organ_term"].queryset = Term.objects.filter(type=VocabularyTermType.organ)
        # self.fields["effect_term"].queryset = Term.objects.filter(type=VocabularyTermType.effect)
        # self.fields["effect_subtype_term"].queryset = Term.objects.filter(type=VocabularyTermType.effect_subtype)

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("system", 4, "col-md-3")
        helper.add_row("effect_modifier_timing", 4, "col-md-3")

        return helper


class ObservationTimeForm(forms.ModelForm):
    class Meta:
        model = models.ObservationTime
        exclude = ()

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        # TODO - right now with name/name_term, the associated dropdown for picking an endpoint shows
        # an empty string for endpoints with a name_term but no freetext name.
        #
        # if we go back to using EHV name_term etc., we need to address this.
        #
        # but also, maybe the ObservationTime UI should be more like the Treatment/DoseGroup formset
        # style, as opposed to separate entry as in the mockup? If we do it that way, then we don't
        # need a UI widget for picking the endpoint at all, b/c it's implicit in the nested structure.
        #
        # in short, right now it's a minor issue, but not worth fixing til we make some other decisions.
        if self.instance.id is not None:
            # editing an existing timepoint
            self.fields["endpoint"].queryset = self.instance.endpoint.experiment.v2_endpoints.all()
        else:
            # creating a new one
            self.fields["endpoint"].queryset = experiment.v2_endpoints.all()

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False

        return helper


class DataExtractionForm(forms.ModelForm):
    class Meta:
        model = models.DataExtraction
        exclude = ("experiment",)

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if experiment:
            self.instance.experiment = experiment
        self.fields["endpoint"].queryset = self.instance.experiment.v2_endpoints.all()
        self.fields["treatment"].queryset = self.instance.experiment.v2_treatments.all()
        self.fields["observation_timepoint"].queryset = models.ObservationTime.objects.filter(
            endpoint__in=self.instance.experiment.v2_endpoints.all()
        )

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("data_location", 3, "col-md-4")
        helper.add_row("statistical_method", 2, "col-md-6")
        helper.add_row("method_to_control_for_litter_effects", 3, "col-md-4")

        return helper

    def is_valid(self):
        if "is_qualitative_only" in self.data and self.data["is_qualitative_only"] == "on":
            # if "is qualitative only" is checked, we are hiding other fields...so relax the required'ness of some...
            for usually_required_field in [
                "dose_response_observations",
                "result_details",
            ]:
                self.fields[usually_required_field].required = False

            # ...and set sensible values on the hidden ones as well.
            hidden_defaults = {
                "data_location": "",
                "dataset_type": "",
                "variance_type": constants.VarianceType.NA,
                "statistical_method": "",
                "statistical_power": "",
                "method_to_control_for_litter_effects": constants.MethodToControlForLitterEffects.NA,
                "values_estimated": False,
                "response_units": "",
                "dose_response_observations": "",
                "result_details": "",
            }

            for field_name in hidden_defaults:
                self.data[field_name] = hidden_defaults[field_name]

        return super().is_valid()


class DoseResponseGroupLevelDataForm(forms.ModelForm):
    formset_parent_key = "data_extraction_id"

    class Meta:
        model = models.DoseResponseGroupLevelData
        exclude = ("data_extraction",)

    def __init__(self, *args, **kwargs):
        data_extraction = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if data_extraction:
            self.instance.data_extraction = data_extraction


class DoseResponseGroupLevelDataFormHelper(BaseFormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.template = "bootstrap4/table_inline_formset.html"


class DoseResponseAnimalLevelDataForm(forms.ModelForm):
    formset_parent_key = "data_extraction_id"

    class Meta:
        model = models.DoseResponseAnimalLevelData
        exclude = ("data_extraction",)

    def __init__(self, *args, **kwargs):
        data_extraction = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if data_extraction:
            self.instance.data_extraction = data_extraction


class DoseResponseAnimalLevelDataFormHelper(BaseFormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.template = "bootstrap4/table_inline_formset.html"
