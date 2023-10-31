import json
from collections import Counter

from crispy_forms import layout as cfl
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelForm
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.urls import reverse

from hawc.apps.udf.models import ModelUDFContent

from ..assessment.autocomplete import DSSToxAutocomplete, EffectTagAutocomplete
from ..common.autocomplete import (
    AutocompleteSelectMultipleWidget,
    AutocompleteSelectWidget,
    AutocompleteTextWidget,
)
from ..common.forms import BaseFormHelper, CopyForm, QuillField
from ..vocab.constants import VocabularyNamespace
from . import autocomplete, constants, models


class ExperimentForm(ModelForm):
    class Meta:
        model = models.Experiment
        exclude = ("study",)
        field_classes = {"description": QuillField}
        widgets = {
            "dtxsid": AutocompleteSelectWidget(autocomplete_class=DSSToxAutocomplete),
            "chemical": AutocompleteTextWidget(
                autocomplete_class=autocomplete.ExperimentAutocomplete, field="chemical"
            ),
            "cas": AutocompleteTextWidget(
                autocomplete_class=autocomplete.ExperimentAutocomplete, field="cas"
            ),
            "chemical_source": AutocompleteTextWidget(
                autocomplete_class=autocomplete.ExperimentAutocomplete, field="chemical_source"
            ),
            "guideline_compliance": AutocompleteTextWidget(
                autocomplete_class=autocomplete.ExperimentAutocomplete, field="guideline_compliance"
            ),
        }

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
        helper.add_row("chemical", 3, "col-md-4")
        helper.add_row("purity_available", 4, ["col-md-2", "col-md-2", "col-md-2", "col-md-6"])
        url = reverse("assessment:dtxsid_create")
        helper.add_create_btn("dtxsid", url, "Add new DTXSID")
        helper.form_id = "experiment-form"
        return helper

    PURITY_QUALIFIER_REQ = "Qualifier must be specified"
    PURITY_QUALIFIER_NOT_REQ = "Qualifier must be blank if purity is not available"
    PURITY_REQ = "A purity value must be specified"
    PURITY_NOT_REQ = "Purity must be blank if purity is not available"

    def clean(self):
        cleaned_data = super().clean()

        purity_available = cleaned_data.get("purity_available")
        purity_qualifier = cleaned_data.get("purity_qualifier")
        purity = cleaned_data.get("purity")

        if purity_available and purity_qualifier == "":
            self.add_error("purity_qualifier", self.PURITY_QUALIFIER_REQ)

        if purity_available and purity is None:
            self.add_error("purity", self.PURITY_REQ)

        if not purity_available and purity_qualifier != "":
            self.add_error("purity_qualifier", self.PURITY_QUALIFIER_NOT_REQ)

        if not purity_available and purity is not None:
            self.add_error("purity", self.PURITY_NOT_REQ)

        return cleaned_data

    def clean_purity_qualifier(self):
        # if None value returned, change to ""
        return self.cleaned_data.get("purity_qualifier", "")


class ExperimentSelectorForm(CopyForm):
    legend_text = "Copy experiment"
    help_text = "Select an existing experiment as a template to create a new one."
    create_url_pattern = "animal:experiment_new"
    selector = forms.ModelChoiceField(
        queryset=models.Experiment.objects.all(), empty_label=None, label="Select template"
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.fields["selector"].queryset = self.fields["selector"].queryset.filter(
            study=self.parent
        )


class AnimalGroupForm(ModelForm):
    class Meta:
        model = models.AnimalGroup
        exclude = ("experiment", "dosing_regime", "generation", "parents")
        labels = {"lifestage_assessed": "Lifestage at assessment"}
        field_classes = {"comments": QuillField}

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)

        if parent:
            self.instance.experiment = parent

        # for lifestage assessed/exposed, use a select widget. Manually add in
        # previously saved values that don't conform to the lifestage choices
        lifestage_dict = dict(constants.Lifestage.choices)
        if self.instance.lifestage_exposed in lifestage_dict:
            le_choices = constants.Lifestage.choices
        else:
            le_choices = [
                (self.instance.lifestage_exposed, self.instance.lifestage_exposed),
                *constants.Lifestage.choices,
            ]
        self.fields["lifestage_exposed"].widget = forms.Select(choices=le_choices)

        if self.instance.lifestage_assessed in lifestage_dict:
            la_choices = constants.Lifestage.choices
        else:
            la_choices = [
                (self.instance.lifestage_assessed, self.instance.lifestage_assessed),
                *constants.Lifestage.choices,
            ]
        self.fields["lifestage_assessed"].widget = forms.Select(choices=la_choices)

        self.fields["siblings"].queryset = models.AnimalGroup.objects.filter(
            experiment=self.instance.experiment
        )

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            widget.attrs["class"] = "form-control"

        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": "Update an existing animal-group.",
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new animal-group",
                "help_text": """
                    Create a new animal-group. Each animal-group is a set of
                    animals which are comparable for a given experiment. For
                    example, they may be a group of F1 rats. Animal-groups may
                    have different exposures or doses, but should be otherwise
                    comparable.""",
                "cancel_url": self.instance.experiment.get_absolute_url(),
            }

        helper = BaseFormHelper(self, **inputs)

        helper.form_id = "animal_group"
        helper.add_row("species", 3, "col-md-4")
        helper.add_row("lifestage_exposed", 2, "col-md-6")

        if "generation" in self.fields:
            helper.add_row("siblings", 3, "col-md-4")

        helper.add_row("comments", 2, "col-md-6")

        assessment_id = self.instance.experiment.study.assessment.pk
        helper.add_create_btn(
            "species", reverse("assessment:species_create", args=(assessment_id,)), "Create species"
        )
        helper.add_create_btn(
            "strain", reverse("assessment:strain_create", args=(assessment_id,)), "Create strain"
        )

        return helper

    STRAIN_NOT_SPECIES = "Selected strain is not of the selected species."

    def clean(self):
        cleaned_data = super().clean()

        species = cleaned_data.get("species")
        strain = cleaned_data.get("strain")
        if strain and species and species != strain.species:
            self.add_error("strain", self.STRAIN_NOT_SPECIES)

        return cleaned_data


class AnimalGroupSelectorForm(CopyForm):
    legend_text = "Copy animal group"
    help_text = "Select an existing animal group as a template to create a new one."
    create_url_pattern = "animal:animal_group_new"
    selector = forms.ModelChoiceField(
        queryset=models.AnimalGroup.objects.all(), empty_label=None, label="Select template"
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.fields["selector"].queryset = self.fields["selector"].queryset.filter(
            experiment=self.parent
        )


class GenerationalAnimalGroupForm(AnimalGroupForm):
    class Meta:
        model = models.AnimalGroup
        exclude = ("experiment",)
        labels = {"lifestage_assessed": "Lifestage at assessment"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["generation"].choices = self.fields["generation"].choices[1:]
        self.fields["parents"].queryset = models.AnimalGroup.objects.filter(
            experiment=self.instance.experiment
        )
        self.fields["dosing_regime"].queryset = models.DosingRegime.objects.filter(
            dosed_animals__in=self.fields["parents"].queryset
        )


class DosingRegimeForm(ModelForm):
    class Meta:
        model = models.DosingRegime
        exclude = ("dosed_animals",)
        field_classes = {"description": QuillField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            self.fields[fld].widget.attrs["class"] = "form-control"

        if self.instance.id:
            inputs = {
                "legend_text": "Update dosing regime",
                "help_text": "Update an existing dosing-regime.",
                "cancel_url": self.instance.dosed_animals.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new dosing-regime",
                "help_text": """
                    Create a new dosing-regime. Each dosing-regime is one
                    protocol for how animals were dosed. Multiple different
                    dose-metrics can be associated with one dosing regime. If
                    this is a generational-experiment, you may not need to create
                    a new dosing-regime, but could instead specify the dosing
                    regime of parents or other ancestors.""",
            }

        helper = BaseFormHelper(self, **inputs)

        helper.form_id = "dosing_regime"
        helper.add_row("duration_exposure", 3, "col-md-4")
        helper.add_row("num_dose_groups", 3, "col-md-4")
        return helper


class DoseGroupForm(ModelForm):
    class Meta:
        model = models.DoseGroup
        fields = ("dose_units", "dose_group_id", "dose")


class BaseDoseGroupFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = models.DoseGroup.objects.none()

    def clean(self, **kwargs):
        """
        Ensure that the selected dose_groups fields have an number of dose_groups
        equal to those expected from the animal dose group, and that all dose
        ids have all dose groups.
        """
        if any(self.errors):
            return

        dose_units = Counter()
        dose_group = Counter()
        num_dose_groups = self.data["num_dose_groups"]
        dose_groups = self.cleaned_data

        if len(dose_groups) < 1:
            raise forms.ValidationError(
                "<ul><li>At least one set of dose-units must be presented!</li></ul>"
            )

        for dose in dose_groups:
            dose_units[dose["dose_units"]] += 1
            dose_group[dose["dose_group_id"]] += 1

        for dose_unit in dose_units.values():
            if dose_unit != num_dose_groups:
                raise forms.ValidationError(
                    f"<ul><li>Each dose-type must have {num_dose_groups} dose groups</li></ul>"
                )

        if not all(list(dose_group.values())[0] == group for group in list(dose_group.values())):
            raise forms.ValidationError(
                "<ul><li>All dose ids must be equal to the same number of values</li></ul>"
            )


def dosegroup_formset_factory(groups, num_dose_groups):
    data = {
        "form-TOTAL_FORMS": str(len(groups)),
        "form-INITIAL_FORMS": 0,
        "num_dose_groups": num_dose_groups,
    }

    for i, v in enumerate(groups):
        data[f"form-{i}-dose_group_id"] = str(v.get("dose_group_id", ""))
        data[f"form-{i}-dose_units"] = str(v.get("dose_units", ""))
        data[f"form-{i}-dose"] = str(v.get("dose", ""))

    FS = modelformset_factory(
        models.DoseGroup,
        form=DoseGroupForm,
        formset=BaseDoseGroupFormSet,
        extra=len(groups),
    )

    return FS(data)


class EndpointForm(ModelForm):
    class Meta:
        model = models.Endpoint
        fields = (
            "name",
            "system",
            "organ",
            "effect",
            "effect_subtype",
            "effects",
            "diagnostic",
            "observation_time",
            "observation_time_units",
            "observation_time_text",
            "data_reported",
            "data_extracted",
            "values_estimated",
            "data_type",
            "variance_type",
            "confidence_interval",
            "response_units",
            "data_location",
            "expected_adversity_direction",
            "NOEL",
            "LOEL",
            "FEL",
            "monotonicity",
            "statistical_test",
            "trend_result",
            "trend_value",
            "power_notes",
            "results_notes",
            "endpoint_notes",
            "litter_effects",
            "litter_effect_notes",
            "name_term",
            "system_term",
            "organ_term",
            "effect_term",
            "effect_subtype_term",
        )
        widgets = {
            "name_term": forms.HiddenInput,
            "system_term": forms.HiddenInput,
            "organ_term": forms.HiddenInput,
            "effect_term": forms.HiddenInput,
            "effect_subtype_term": forms.HiddenInput,
            "effects": AutocompleteSelectMultipleWidget(autocomplete_class=EffectTagAutocomplete),
            "statistical_test": AutocompleteTextWidget(
                autocomplete_class=autocomplete.EndpointAutocomplete, field="statistical_test"
            ),
        }
        field_classes = {"results_notes": QuillField, "endpoint_notes": QuillField}

    def __init__(self, *args, **kwargs):
        animal_group = kwargs.pop("parent", None)
        assessment = kwargs.pop("assessment", None)
        super().__init__(*args, **kwargs)

        self.fields["effects"].label = "Additional tags"
        self.fields[
            "effects"
        ].help_text = "Any additional descriptive-tags used to categorize the outcome"

        self.fields["NOEL"].widget = forms.Select()
        self.fields["LOEL"].widget = forms.Select()
        self.fields["FEL"].widget = forms.Select()

        noel_names = assessment.get_noel_names() if assessment else self.instance.get_noel_names()
        self.fields["NOEL"].label = noel_names.noel
        self.fields["NOEL"].help_text = noel_names.noel_help_text
        self.fields["LOEL"].label = noel_names.loel
        self.fields["LOEL"].help_text = noel_names.loel_help_text

        if animal_group:
            self.instance.animal_group = animal_group
            self.instance.assessment = assessment

        self.noel_names = json.dumps(self.instance.get_noel_names()._asdict())

        # User Defined Form
        if assessment is None:
            assessment = self.instance.get_assessment()
        self.model_binding = assessment.get_model_binding(self.Meta.model)
        if self.model_binding:
            try:
                udf_content = self.model_binding.saved_contents.get(object_id=self.instance.id)
                initial = udf_content.content
            except ModelUDFContent.DoesNotExist:
                initial = None

            udf = self.model_binding.form_field(label="User defined fields", initial=initial)
            self.fields["udf"] = udf

    @property
    def helper(self):
        vocab_enabled = self.instance.assessment.vocabulary == VocabularyNamespace.EHV
        if vocab_enabled:
            vocab = f"""&nbsp;The <a href="{reverse('vocab:ehv-browse')}">Environmental
                Health Vocabulary (EHV)</a> is enabled for this assessment. Browse to view
                controlled terms, and whenever possible please use these terms."""
        else:
            vocab = f"""&nbsp;A controlled vocabulary is not enabled for this assessment.
                However, you can still browse the <a href="{reverse('vocab:ehv-browse')}">Environmental
                Health Vocabulary (EHV)</a> to see if this vocabulary would be a good fit for your
                assessment. If it is, consider updating the assessment to use this vocabulary."""

        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": f"Update an existing endpoint.{vocab}",
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new endpoint",
                "help_text": f"""Create a new endpoint. An endpoint may should describe one
                    measure-of-effect which was measured in the study. It may
                    or may not contain quantitative data.{vocab}""",
                "cancel_url": self.instance.animal_group.get_absolute_url(),
            }

        helper = BaseFormHelper(self, **inputs)

        helper.form_id = "endpoint"

        self.fields["diagnostic"].widget.attrs["rows"] = 2
        for fld in ("results_notes", "endpoint_notes", "power_notes"):
            self.fields[fld].widget.attrs["rows"] = 3

        # by default take-up the whole row
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs["class"] = "form-control"

        helper.layout.insert(
            helper.find_layout_idx_for_field_name("name"),
            cfl.Div(id="vocab"),
        )
        helper.add_row("name", 1, "col-md-12")
        helper.add_row("system", 4, "col-md-3")
        helper.add_row("effects", 2, "col-md-6")
        helper.add_row("observation_time", 3, "col-md-4")
        helper.add_row("data_reported", 3, "col-md-4")
        helper.add_row("data_type", 3, "col-md-4")
        helper.add_row("response_units", 3, "col-md-4")
        helper.add_row("NOEL", 4, "col-md-3")
        helper.add_row("statistical_test", 3, ["col-md-6", "col-md-3", "col-md-3"])
        helper.add_row("litter_effects", 2, "col-md-6")
        helper.add_row("name_term", 5, "col-md-2")

        url = reverse("assessment:effect_tag_create", kwargs={"pk": self.instance.assessment.pk})
        helper.add_create_btn("effects", url, "Add new effect tag")
        helper.attrs["class"] = "hidden"
        return helper

    LIT_EFF_REQ = "Litter effects required if a reproductive/developmental study"
    LIT_EFF_NOT_REQ = "Litter effects must be NA if non-reproductive/developmental study"
    LIT_EFF_NOTES_REQ = 'Notes are required if litter effects are "Other"'
    LIT_EFF_NOTES_NOT_REQ = "Litter effect notes should be blank if effects are not-applicable"
    OBS_TIME_UNITS_REQ = "If reporting an endpoint-observation time, time-units must be specified."
    OBS_TIME_VALUE_REQ = "An observation-time must be reported if time-units are specified"
    CONF_INT_REQ = "Confidence-interval is required for" "percent-difference data"
    VAR_TYPE_REQ = "If entering continuous data, the variance type must be SD (standard-deviation) or SE (standard error)"
    RESP_UNITS_REQ = "If data is extracted, response-units are required"
    NAME_REQ = "Endpoint/Adverse outcome is required"

    @classmethod
    def clean_endpoint(cls, instance: models.Endpoint, data: dict) -> dict:
        """Full dataset clean; used for both form and serializer.

        Args:
            instance (models.Endpoint): an Endpoint instance (can be unsaved)
            data (dict): form/serializer data

        Returns:
            dict: A dictionary of errors; may be empty
        """
        errors: dict[str, str] = {}

        obs_time = data.get("observation_time", None)
        observation_time_units = data.get("observation_time_units", 0)

        if obs_time is not None and observation_time_units == constants.ObservationTimeUnits.NR:
            errors["observation_time_units"] = cls.OBS_TIME_UNITS_REQ

        if obs_time is None and observation_time_units > 0:
            errors["observation_time"] = cls.OBS_TIME_VALUE_REQ

        litter_effects = data.get("litter_effects", "NA")
        litter_effect_notes = data.get("litter_effect_notes", "")

        if instance.litter_effect_required():
            if litter_effects == "NA":
                errors["litter_effects"] = cls.LIT_EFF_REQ

        elif not instance.litter_effect_optional() and litter_effects != "NA":
            errors["litter_effects"] = cls.LIT_EFF_NOT_REQ

        if litter_effects == "O" and litter_effect_notes == "":
            errors["litter_effect_notes"] = cls.LIT_EFF_NOTES_REQ

        if litter_effects == "NA" and litter_effect_notes != "":
            errors["litter_effect_notes"] = cls.LIT_EFF_NOTES_NOT_REQ

        confidence_interval = data.get("confidence_interval", None)
        variance_type = data.get("variance_type", 0)
        data_type = data.get("data_type", constants.DataType.CONTINUOUS)
        if data_type == constants.DataType.PERCENT_DIFFERENCE and confidence_interval is None:
            errors["confidence_interval"] = cls.CONF_INT_REQ

        if (
            data_type == constants.DataType.CONTINUOUS
            and variance_type == constants.VarianceType.NA
        ):
            errors["variance_type"] = cls.VAR_TYPE_REQ

        response_units = data.get("response_units", "")
        data_extracted = data.get("data_extracted", True)
        if data_extracted and response_units == "":
            errors["response_units"] = cls.RESP_UNITS_REQ

        return errors

    def clean(self):
        cleaned_data = super().clean()

        errors = self.clean_endpoint(self.instance, cleaned_data)
        for key, value in errors.items():
            self.add_error(key, value)

        # the name input is hidden and overridden, so any "name" field error
        # must be displayed instead as a non_field_error
        name_error = self.errors.get("name", None)
        if name_error is not None:
            self.add_error(None, self.NAME_REQ)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit and "udf" in self.changed_data:
            ModelUDFContent.objects.update_or_create(
                defaults=dict(content=self.cleaned_data["udf"]),
                model_binding=self.model_binding,
                content_type=self.model_binding.content_type,
                object_id=instance.id,
            )
        return instance


class EndpointGroupForm(forms.ModelForm):
    class Meta:
        exclude = ("endpoint", "dose_group_id", "significant")
        model = models.EndpointGroup

    def __init__(self, *args, **kwargs):
        endpoint = kwargs.pop("endpoint", None)
        super().__init__(*args, **kwargs)
        if endpoint:
            self.instance.endpoint = endpoint
        for fld in self.fields:
            self.fields[fld].widget.attrs["class"] = "form-control"

    VARIANCE_REQ = (
        'Variance must be numeric, or the endpoint-field "variance-type" should be "not reported"'
    )
    LOWER_CI_REQ = "A lower CI must be provided if an upper CI is provided"
    LOWER_CI_GT_UPPER = "Lower CI must be less-than or equal to upper CI"
    UPPER_CI_REQ = "An upper CI must be provided if an lower CI is provided"
    INC_REQ = "An Incidence must be provided if an N is provided"
    N_REQ = "An N must be provided if an Incidence is provided"
    POS_N_REQ = "Incidence must be less-than or equal-to N"

    @classmethod
    def clean_endpoint_group(cls, data_type: str, variance_type: int, data: dict) -> dict:
        """Endpoint group clean; used for both form and serializer.

        Args:
            data_type (str): Endpoint.data_type
            variance_type (int): Endpoint.variance_type
            data (dict): form/serializer data

        Returns:
            dict: A dictionary of errors; may be empty
        """
        errors: dict[str, str] = {}

        if data_type == constants.DataType.CONTINUOUS:
            var = data.get("variance")
            if var is not None and variance_type in (0, 3):
                errors["variance"] = cls.VARIANCE_REQ
        elif data_type == constants.DataType.PERCENT_DIFFERENCE:
            lower_ci = data.get("lower_ci")
            upper_ci = data.get("upper_ci")
            if lower_ci is None and upper_ci is not None:
                errors["lower_ci"] = cls.LOWER_CI_REQ
            if lower_ci is not None and upper_ci is None:
                errors["upper_ci"] = cls.UPPER_CI_REQ
            if lower_ci is not None and upper_ci is not None and lower_ci > upper_ci:
                errors["lower_ci"] = cls.LOWER_CI_GT_UPPER
        elif data_type in [constants.DataType.DICHOTOMOUS, constants.DataType.DICHOTOMOUS_CANCER]:
            if data.get("incidence") is None and data.get("n") is not None:
                errors["incidence"] = cls.INC_REQ
            if data.get("incidence") is not None and data.get("n") is None:
                errors["n"] = cls.N_REQ
            if (
                data.get("incidence") is not None
                and data.get("n") is not None
                and data["incidence"] > data["n"]
            ):
                errors["incidence"] = cls.POS_N_REQ

        return errors

    def clean(self):
        cleaned_data = super().clean()
        data_type = self.endpoint_form.cleaned_data["data_type"]
        variance_type = self.endpoint_form.cleaned_data.get("variance_type", 0)

        errors = self.clean_endpoint_group(data_type, variance_type, cleaned_data)
        for key, value in errors.items():
            self.add_error(key, value)

        return cleaned_data


class BaseEndpointGroupFormSet(BaseModelFormSet):
    def __init__(self, **defaults):
        super().__init__(**defaults)
        if len(self.forms) > 0:
            self.forms[0].fields["significance_level"].widget.attrs["class"] += " hidden"


EndpointGroupFormSet = modelformset_factory(
    models.EndpointGroup,
    form=EndpointGroupForm,
    formset=BaseEndpointGroupFormSet,
    extra=0,
)


class EndpointSelectorForm(CopyForm):
    legend_text = "Copy endpoint"
    help_text = "Select an existing endpoint as a template to create a new one."
    create_url_pattern = "animal:endpoint_new"
    selector = forms.ModelChoiceField(
        queryset=models.Endpoint.objects.all(), empty_label=None, label="Select template"
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.fields["selector"].queryset = (
            self.fields["selector"]
            .queryset.filter(animal_group__experiment__study=self.parent.experiment.study_id)
            .select_related("animal_group__experiment")
            .order_by("animal_group__experiment__name", "animal_group__name", "name")
        )
        self.fields["selector"].label_from_instance = (
            lambda obj: f"{obj.animal_group.experiment} | {obj.animal_group} | {obj}"
        )


class MultipleEndpointChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.label
