import json
from collections import Counter

from crispy_forms import bootstrap as cfb
from crispy_forms import layout as cfl
from django import forms
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import ModelForm
from django.forms.models import BaseModelFormSet, modelformset_factory
from selectable import forms as selectable

from ..assessment.lookups import EffectTagLookup, SpeciesLookup, StrainLookup
from ..assessment.models import DoseUnits
from ..common.forms import BaseFormHelper, CopyAsNewSelectorForm
from ..common.models import get_flavored_text
from ..study.lookups import AnimalStudyLookup
from . import lookups, models


class ExperimentForm(ModelForm):
    class Meta:
        model = models.Experiment
        exclude = ("study",)

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if parent:
            self.instance.study = parent

        self.fields["chemical"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.ExpChemicalLookup, allow_new=True
        )

        self.fields["cas"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.ExpCasLookup, allow_new=True
        )

        self.fields["chemical_source"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.ExpChemSourceLookup, allow_new=True
        )

        self.fields["guideline_compliance"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.ExpGlpLookup, allow_new=True
        )

        # change checkbox to select box
        self.fields["has_multiple_generations"].widget = forms.Select(
            choices=((True, "Yes"), (False, "No"))
        )

        self.helper = self.setHelper()

    def setHelper(self):

        # by default take-up the whole row-fluid
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs["class"] = "span12"

        self.fields["description"].widget.attrs["rows"] = 4

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
        helper.form_class = None
        helper.add_fluid_row("name", 3, "span4")
        helper.add_fluid_row("chemical", 3, "span4")
        helper.add_fluid_row("purity_available", 4, ["span2", "span2", "span2", "span6"])
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


class ExperimentSelectorForm(CopyAsNewSelectorForm):
    label = "Experiment"
    lookup_class = lookups.ExperimentByStudyLookup


class AnimalGroupForm(ModelForm):
    class Meta:
        model = models.AnimalGroup
        exclude = ("experiment", "dosing_regime", "generation", "parents")
        labels = {"lifestage_assessed": "Lifestage at assessment"}

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)

        if parent:
            self.instance.experiment = parent

        # for lifestage assessed/exposed, use a select widget. Manually add in
        # previously saved values that don't conform to the LIFESTAGE_CHOICES tuple
        lifestage_dict = dict(models.AnimalGroup.LIFESTAGE_CHOICES)

        if self.instance.lifestage_exposed in lifestage_dict:
            le_choices = models.AnimalGroup.LIFESTAGE_CHOICES
        else:
            le_choices = (
                (self.instance.lifestage_exposed, self.instance.lifestage_exposed),
            ) + models.AnimalGroup.LIFESTAGE_CHOICES
        self.fields["lifestage_exposed"].widget = forms.Select(choices=le_choices)

        if self.instance.lifestage_assessed in lifestage_dict:
            la_choices = models.AnimalGroup.LIFESTAGE_CHOICES
        else:
            la_choices = (
                (self.instance.lifestage_assessed, self.instance.lifestage_assessed),
            ) + models.AnimalGroup.LIFESTAGE_CHOICES
        self.fields["lifestage_assessed"].widget = forms.Select(choices=la_choices)

        self.fields["siblings"].queryset = models.AnimalGroup.objects.filter(
            experiment=self.instance.experiment
        )

        self.helper = self.setHelper()
        self.fields["comments"].widget.attrs["rows"] = 4

    def setHelper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if fld in ["species", "strain"]:
                widget.attrs["class"] = "span10"
            else:
                widget.attrs["class"] = "span12"

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
        helper.form_class = None
        helper.form_id = "animal_group"
        helper.add_fluid_row("species", 3, "span4")
        helper.add_fluid_row("lifestage_exposed", 2, "span6")

        assessment_id = self.instance.experiment.study.assessment.pk

        url = reverse("assessment:species_create", kwargs={"pk": assessment_id})
        helper.addBtnLayout(helper.layout[3], 0, url, "Add new species", "span4")

        url = reverse("assessment:strain_create", kwargs={"pk": assessment_id})
        helper.addBtnLayout(helper.layout[3], 1, url, "Add new strain", "span4")

        if "generation" in self.fields:
            helper.add_fluid_row("siblings", 3, "span4")

        helper.add_fluid_row("comments", 2, "span6")

        return helper

    def clean(self):
        cleaned_data = super().clean()

        species = cleaned_data.get("species")
        strain = cleaned_data.get("strain")
        if strain and species and species != strain.species:
            err = "Selected strain is not of the selected species."
            self.add_error("strain", err)

        return cleaned_data


class AnimalGroupSelectorForm(CopyAsNewSelectorForm):
    label = "Animal group"
    lookup_class = lookups.AnimalGroupByExperimentLookup


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.setHelper()

    def setHelper(self):

        self.fields["description"].widget.attrs["rows"] = 4
        for fld in list(self.fields.keys()):
            self.fields[fld].widget.attrs["class"] = "span12"

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
        helper.form_class = None
        helper.form_id = "dosing_regime"
        helper.add_fluid_row("duration_exposure", 3, "span4")
        helper.add_fluid_row("num_dose_groups", 3, "span4")
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
        models.DoseGroup, form=DoseGroupForm, formset=BaseDoseGroupFormSet, extra=len(groups),
    )

    return FS(data)


class EndpointForm(ModelForm):

    effects = selectable.AutoCompleteSelectMultipleField(
        lookup_class=EffectTagLookup,
        required=False,
        help_text=get_flavored_text("ani__endpoint_form__effects"),
        label="Additional tags",
    )

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
        )

    def __init__(self, *args, **kwargs):
        animal_group = kwargs.pop("parent", None)
        assessment = kwargs.pop("assessment", None)
        super().__init__(*args, **kwargs)

        self.fields["NOEL"].widget = forms.Select()
        self.fields["LOEL"].widget = forms.Select()
        self.fields["FEL"].widget = forms.Select()

        noel_names = assessment.get_noel_names() if assessment else self.instance.get_noel_names()
        self.fields["NOEL"].label = noel_names.noel
        self.fields["NOEL"].help_text = noel_names.noel_help_text
        self.fields["LOEL"].label = noel_names.loel
        self.fields["LOEL"].help_text = noel_names.loel_help_text

        self.fields["system"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.EndpointSystemLookup, allow_new=True
        )

        self.fields["organ"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.EndpointOrganLookup, allow_new=True
        )

        self.fields["effect"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.EndpointEffectLookup, allow_new=True
        )

        self.fields["effect_subtype"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.EndpointEffectSubtypeLookup, allow_new=True
        )

        self.fields["statistical_test"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.EndpointStatisticalTestLookup, allow_new=True
        )

        if animal_group:
            self.instance.animal_group = animal_group
            self.instance.assessment = assessment

        self.fields["name"].help_text = get_flavored_text("ani__endpoint_form__name")

        self.helper = self.setHelper()

        self.noel_names = json.dumps(self.instance.get_noel_names()._asdict())

    def setHelper(self):
        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": "Update an existing endpoint.",
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new endpoint",
                "help_text": get_flavored_text("ani__endpoint_form__create"),
                "cancel_url": self.instance.animal_group.get_absolute_url(),
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        helper.form_id = "endpoint"

        self.fields["diagnostic"].widget.attrs["rows"] = 2
        for fld in ("results_notes", "endpoint_notes", "power_notes"):
            self.fields[fld].widget.attrs["rows"] = 3

        # by default take-up the whole row-fluid
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                if fld in ["effects"]:
                    widget.attrs["class"] = "span10"
                else:
                    widget.attrs["class"] = "span12"

        helper.add_fluid_row("system", 4, "span3")
        helper.add_fluid_row("effects", 2, "span6")
        helper.add_fluid_row("observation_time", 3, "span4")
        helper.add_fluid_row("data_reported", 3, "span4")
        helper.add_fluid_row("data_type", 3, "span4")
        helper.add_fluid_row("response_units", 3, "span4")
        helper.add_fluid_row("NOEL", 4, "span3")
        helper.add_fluid_row("statistical_test", 3, ["span6", "span3", "span3"])
        helper.add_fluid_row("litter_effects", 2, "span6")

        url = reverse("assessment:effect_tag_create", kwargs={"pk": self.instance.assessment.pk})
        helper.addBtnLayout(helper.layout[4], 0, url, "Add new effect tag", "span6")

        return helper

    LIT_EFF_REQ = "Litter effects required if a reproductive/developmental study"
    LIT_EFF_NOT_REQ = "Litter effects must be NA if non-reproductive/developmental study"
    LIT_EFF_NOTES_REQ = 'Notes are required if litter effects are "Other"'
    LIT_EFF_NOTES_NOT_REQ = "Litter effect notes should be blank if effects are not-applicable"

    def clean(self):
        cleaned_data = super().clean()
        obs_time = cleaned_data.get("observation_time")
        observation_time_units = cleaned_data.get("observation_time_units")
        litter_effects = cleaned_data.get("litter_effects")
        litter_effect_notes = cleaned_data.get("litter_effect_notes")

        if obs_time is not None and observation_time_units == 0:
            err = "If reporting an endpoint-observation time, time-units must be specified."
            self.add_error("observation_time_units", err)

        if obs_time is None and observation_time_units > 0:
            err = "An observation-time must be reported if time-units are specified"
            self.add_error("observation_time", err)

        if self.instance.litter_effect_required():
            if litter_effects == "NA":
                self.add_error("litter_effects", self.LIT_EFF_REQ)
        elif not self.instance.litter_effect_optional() and litter_effects != "NA":
            self.add_error("litter_effects", self.LIT_EFF_NOT_REQ)

        if litter_effects == "O" and litter_effect_notes == "":
            self.add_error("litter_effect_notes", self.LIT_EFF_NOTES_REQ)

        if litter_effects == "NA" and litter_effect_notes != "":
            self.add_error("litter_effect_notes", self.LIT_EFF_NOTES_NOT_REQ)

        return cleaned_data

    def clean_confidence_interval(self):
        confidence_interval = self.cleaned_data["confidence_interval"]
        data_type = self.cleaned_data.get("data_type")
        if data_type == "P" and confidence_interval is None:
            raise forms.ValidationError(
                "Confidence-interval is required for" "percent-difference data"
            )
        return confidence_interval

    def clean_variance_type(self):
        data_type = self.cleaned_data.get("data_type")
        variance_type = self.cleaned_data.get("variance_type")
        if data_type == "C" and variance_type == 0:
            raise forms.ValidationError(
                "If entering continuous data, the variance type must be SD"
                "(standard-deviation) or SE (standard error)"
            )
        return variance_type

    def clean_response_units(self):
        response_units = self.cleaned_data.get("response_units")
        data_extracted = self.cleaned_data.get("data_extracted")
        if data_extracted and response_units == "":
            raise forms.ValidationError(
                "If data is extracted (see checkbox), response-units are required"
            )
        return response_units


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
            self.fields[fld].widget.attrs["class"] = "span12"

    def clean(self):
        super().clean()
        data = self.cleaned_data
        data_type = self.endpoint_form.cleaned_data["data_type"]
        var_type = self.endpoint_form.cleaned_data.get("variance_type", 0)

        if data_type == "C":
            var = data.get("variance")
            if var is not None and var_type in (0, 3):
                msg = 'Variance must be numeric, or the endpoint-field "variance-type" should be "not reported"'
                self.add_error("variance", msg)
        elif data_type == "P":
            if data.get("lower_ci") is None and data.get("upper_ci") is not None:
                msg = "A lower CI must be provided if an upper CI is provided"
                self.add_error("lower_ci", msg)
            if data.get("lower_ci") is not None and data.get("upper_ci") is None:
                msg = "An upper CI must be provided if an lower CI is provided"
                self.add_error("upper_ci", msg)
        elif data_type in ["D", "DC"]:
            if data.get("incidence") is None and data.get("n") is not None:
                msg = "An Incidence must be provided if an N is provided"
                self.add_error("incidence", msg)
            if data.get("incidence") is not None and data.get("n") is None:
                msg = "An N must be provided if an Incidence is provided"
                self.add_error("n", msg)
            if (
                data.get("incidence") is not None
                and data.get("n") is not None
                and data["incidence"] > data["n"]
            ):
                msg = "Incidence must be less-than or equal-to N"
                self.add_error("incidence", msg)

        return data


class BaseEndpointGroupFormSet(BaseModelFormSet):
    def __init__(self, **defaults):
        super().__init__(**defaults)
        if len(self.forms) > 0:
            self.forms[0].fields["significance_level"].widget.attrs["class"] += " hidden"


EndpointGroupFormSet = modelformset_factory(
    models.EndpointGroup, form=EndpointGroupForm, formset=BaseEndpointGroupFormSet, extra=0,
)


class EndpointSelectorForm(CopyAsNewSelectorForm):
    label = "Endpoint"
    lookup_class = lookups.EndpointByStudyLookup


class UploadFileForm(forms.Form):
    file = forms.FileField()


class EndpointFilterForm(forms.Form):

    ORDER_BY_CHOICES = [
        ("animal_group__experiment__study__short_citation", "study"),
        ("animal_group__experiment__name", "experiment name"),
        ("animal_group__name", "animal group"),
        ("name", "endpoint name"),
        ("animal_group__dosing_regime__doses__dose_units_id", "dose units"),
        ("system", "system"),
        ("organ", "organ"),
        ("effect", "effect"),
        ["-NOEL", "<NOEL-NAME>"],
        ["-LOEL", "<LOEL-NAME>"],
        # BMD/BMDL is stored in output which is a JsonField on the bmd Model object. We want to sort on a sub-field of that.
        # when/if HAWC upgrades to Django 2.1 (see yekta's comment on https://stackoverflow.com/questions/36641759/django-1-9-jsonfield-order-by)
        # could possibly do something like this instead.
        # for now we use a custom sort string and handle it in EndpointList class
        # ('bmd_model__model__output__-BMD', 'BMD'),
        # ('bmd_model__model__output__-BMDL', 'BMDLS'),
        ("customBMD", "BMD"),
        ("customBMDLS", "BMDLS"),
        ("effect_subtype", "effect subtype"),
        ("animal_group__experiment__chemical", "chemical"),
    ]

    studies = selectable.AutoCompleteSelectMultipleField(
        label="Study reference",
        lookup_class=AnimalStudyLookup,
        help_text="ex: Smith et al. 2010",
        required=False,
    )

    chemical = forms.CharField(
        label="Chemical name",
        widget=selectable.AutoCompleteWidget(lookups.ExpChemicalLookup),
        help_text="ex: sodium",
        required=False,
    )

    cas = forms.CharField(
        label="CAS",
        widget=selectable.AutoCompleteWidget(lookups.RelatedExperimentCASLookup),
        help_text="ex: 107-02-8",
        required=False,
    )

    lifestage_exposed = forms.CharField(
        label="Lifestage exposed",
        widget=selectable.AutoCompleteWidget(lookups.RelatedAnimalGroupLifestageExposedLookup),
        help_text="ex: pup",
        required=False,
    )

    lifestage_assessed = forms.CharField(
        label="Lifestage assessed",
        widget=selectable.AutoCompleteWidget(lookups.RelatedAnimalGroupLifestageAssessedLookup),
        help_text="ex: adult",
        required=False,
    )

    species = selectable.AutoCompleteSelectField(
        label="Species", lookup_class=SpeciesLookup, help_text="ex: Mouse", required=False,
    )

    strain = selectable.AutoCompleteSelectField(
        label="Strain", lookup_class=StrainLookup, help_text="ex: B6C3F1", required=False,
    )

    sex = forms.MultipleChoiceField(
        choices=models.AnimalGroup.SEX_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        initial=[c[0] for c in models.AnimalGroup.SEX_CHOICES],
        required=False,
    )

    data_extracted = forms.ChoiceField(
        choices=((True, "Yes"), (False, "No"), (None, "All data")), initial=None, required=False,
    )

    name = forms.CharField(
        label="Endpoint name",
        widget=selectable.AutoCompleteWidget(lookups.EndpointByAssessmentTextLookup),
        help_text="ex: heart weight",
        required=False,
    )

    system = forms.CharField(
        label="System",
        widget=selectable.AutoCompleteWidget(lookups.RelatedEndpointSystemLookup),
        help_text="ex: endocrine",
        required=False,
    )

    organ = forms.CharField(
        label="Organ",
        widget=selectable.AutoCompleteWidget(lookups.RelatedEndpointOrganLookup),
        help_text="ex: pituitary",
        required=False,
    )

    effect = forms.CharField(
        label="Effect",
        widget=selectable.AutoCompleteWidget(lookups.RelatedEndpointEffectLookup),
        help_text="ex: alanine aminotransferase (ALT)",
        required=False,
    )

    effect_subtype = forms.CharField(
        label="Effect Subtype",
        widget=selectable.AutoCompleteWidget(lookups.RelatedEndpointEffectSubtypeLookup),
        help_text="ex: ",
        required=False,
    )

    tags = forms.CharField(
        label="Tags",
        widget=selectable.AutoCompleteWidget(EffectTagLookup),
        help_text="ex: antibody response",
        required=False,
    )

    dose_units = forms.ModelChoiceField(queryset=DoseUnits.objects.all(), required=False)

    order_by = forms.ChoiceField(choices=ORDER_BY_CHOICES,)

    paginate_by = forms.IntegerField(
        label="Items per page", min_value=1, initial=25, max_value=10000, required=False
    )

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("assessment")
        super().__init__(*args, **kwargs)
        noel_names = assessment.get_noel_names()

        for field in self.fields:
            if field not in ("sex", "data_extracted", "dose_units", "order_by", "paginate_by",):
                self.fields[field].widget.update_query_parameters({"related": assessment.id})

        for i, (k, v) in enumerate(self.fields["order_by"].choices):
            if v == "<NOEL-NAME>":
                self.fields["order_by"].choices[i][1] = noel_names.noel
                self.fields["order_by"].widget.choices[i][1] = noel_names.noel
            elif v == "<LOEL-NAME>":
                self.fields["order_by"].choices[i][1] = noel_names.loel
                self.fields["order_by"].widget.choices[i][1] = noel_names.loel

        self.helper = self.setHelper()

    def setHelper(self):

        # by default take-up the whole row-fluid
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) not in [forms.CheckboxInput, forms.CheckboxSelectMultiple]:
                widget.attrs["class"] = "span12"

        helper = BaseFormHelper(self)

        helper.form_method = "GET"
        helper.form_class = None

        helper.add_fluid_row("studies", 4, "span3")
        helper.add_fluid_row("species", 4, "span3")
        helper.add_fluid_row("name", 4, "span3")
        helper.add_fluid_row("tags", 4, "span3")

        helper.layout.append(cfb.FormActions(cfl.Submit("submit", "Apply filters"),))

        return helper

    def get_query(self):

        studies = self.cleaned_data.get("studies")
        chemical = self.cleaned_data.get("chemical")
        cas = self.cleaned_data.get("cas")
        lifestage_exposed = self.cleaned_data.get("lifestage_exposed")
        lifestage_assessed = self.cleaned_data.get("lifestage_assessed")
        species = self.cleaned_data.get("species")
        strain = self.cleaned_data.get("strain")
        sex = self.cleaned_data.get("sex")
        data_extracted = self.cleaned_data.get("data_extracted")
        name = self.cleaned_data.get("name")
        system = self.cleaned_data.get("system")
        organ = self.cleaned_data.get("organ")
        effect = self.cleaned_data.get("effect")
        effect_subtype = self.cleaned_data.get("effect_subtype")
        NOEL = self.cleaned_data.get("NOEL")
        LOEL = self.cleaned_data.get("LOEL")
        tags = self.cleaned_data.get("tags")
        dose_units = self.cleaned_data.get("dose_units")

        query = Q()
        if studies:
            query &= Q(animal_group__experiment__study__in=studies)
        if chemical:
            query &= Q(animal_group__experiment__chemical__icontains=chemical)
        if cas:
            query &= Q(animal_group__experiment__cas__icontains=cas)
        if lifestage_exposed:
            query &= Q(animal_group__lifestage_exposed__icontains=lifestage_exposed)
        if lifestage_assessed:
            query &= Q(animal_group__lifestage_assessed__icontains=lifestage_assessed)
        if species:
            query &= Q(animal_group__species=species)
        if strain:
            query &= Q(animal_group__strain__name__icontains=strain.name)
        if sex:
            query &= Q(animal_group__sex__in=sex)
        if data_extracted:
            query &= Q(data_extracted=data_extracted == "True")
        if name:
            query &= Q(name__icontains=name)
        if system:
            query &= Q(system__icontains=system)
        if organ:
            query &= Q(organ__icontains=organ)
        if effect:
            query &= Q(effect__icontains=effect)
        if effect_subtype:
            query &= Q(effect_subtype__icontains=effect_subtype)
        if NOEL:
            query &= Q(NOEL__icontains=NOEL)
        if LOEL:
            query &= Q(LOEL__icontains=LOEL)
        if tags:
            query &= Q(effects__name__icontains=tags)
        if dose_units:
            query &= Q(animal_group__dosing_regime__doses__dose_units=dose_units)
        return query

    def get_order_by(self):
        return self.cleaned_data.get("order_by", self.ORDER_BY_CHOICES[0][0])

    def get_dose_units_id(self):
        if hasattr(self, "cleaned_data") and self.cleaned_data.get("dose_units"):
            return self.cleaned_data.get("dose_units").id
