import json

from django import forms
from django.forms.models import BaseModelFormSet, inlineformset_factory, modelformset_factory
from django.forms.widgets import Select
from django.urls import reverse

from ..assessment.autocomplete import DSSToxAutocomplete, EffectTagAutocomplete
from ..common.autocomplete import (
    AutocompleteSelectMultipleWidget,
    AutocompleteSelectWidget,
    AutocompleteTextWidget,
)
from ..common.forms import BaseFormHelper
from . import autocomplete, models


class IVChemicalForm(forms.ModelForm):
    HELP_TEXT_CREATE = "Describes the chemical used in the current experiment."
    HELP_TEXT_UPDATE = "Update an existing chemical."

    source = forms.CharField(
        label="Source of chemical",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVChemicalAutocomplete, field="source"
        ),
    )

    class Meta:
        model = models.IVChemical
        exclude = ("study",)
        widgets = {
            "dtxsid": AutocompleteSelectWidget(DSSToxAutocomplete),
        }

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study

        self.fields["source"].widget.update_filters(
            {"study__assessment_id": self.instance.study.assessment_id}
        )

    @property
    def helper(self):
        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new experimental chemical",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.instance.study.get_absolute_url(),
            }

        helper = BaseFormHelper(self, **inputs)
        helper.set_textarea_height()
        helper.add_row("cas", 2, "col-md-6")
        helper.add_row("cas_inferred", 2, "col-md-6")
        helper.add_row("source", 3, "col-md-4")
        helper.add_row("purity_confirmed_notes", 2, "col-md-6")
        helper.add_create_btn("dtxsid", reverse("assessment:dtxsid_create"), "Add new DTXSID")
        helper.form_id = "ivchemical-form"

        return helper


class IVCellTypeForm(forms.ModelForm):
    HELP_TEXT_CREATE = "Describes the cell type used in the current experiment."
    HELP_TEXT_UPDATE = "Update an existing cell type."

    species = forms.CharField(
        label="Species",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVCellTypeAutocomplete, field="species"
        ),
    )
    strain = forms.CharField(
        label="Strain",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVCellTypeAutocomplete, field="strain"
        ),
    )
    cell_type = forms.CharField(
        label="Cell type",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVCellTypeAutocomplete, field="cell_type"
        ),
    )
    tissue = forms.CharField(
        label="Tissue",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVCellTypeAutocomplete, field="tissue"
        ),
    )
    source = forms.CharField(
        label="Source of cell cultures",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVCellTypeAutocomplete, field="source"
        ),
    )

    class Meta:
        model = models.IVCellType
        exclude = ("study",)

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study

        for field in ("species", "strain", "cell_type", "tissue", "source"):
            self.fields[field].widget.update_filters(
                {"study__assessment_id": self.instance.study.assessment.id}
            )

    @property
    def helper(self):
        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new cell type",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.instance.study.get_absolute_url(),
            }

        helper = BaseFormHelper(self, **inputs)
        helper.set_textarea_height()
        helper.add_row("species", 3, "col-md-4")
        helper.add_row("cell_type", 2, "col-md-6")
        helper.add_row("tissue", 2, "col-md-6")

        return helper


class IVExperimentForm(forms.ModelForm):
    HELP_TEXT_CREATE = ""
    HELP_TEXT_UPDATE = "Update an existing experiment."

    transfection = forms.CharField(
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVExperimentAutocomplete, field="transfection"
        )
    )
    positive_control = forms.CharField(
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVExperimentAutocomplete, field="positive_control"
        )
    )
    negative_control = forms.CharField(
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVExperimentAutocomplete, field="negative_control"
        )
    )
    vehicle_control = forms.CharField(
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVExperimentAutocomplete, field="vehicle_control"
        )
    )

    class Meta:
        model = models.IVExperiment
        exclude = ("study",)

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study
        self.fields["cell_type"].queryset = self.fields["cell_type"].queryset.filter(
            study=self.instance.study
        )

        for field in (
            "transfection",
            "positive_control",
            "negative_control",
            "vehicle_control",
        ):
            self.fields[field].widget.update_filters(
                {"study__assessment_id": self.instance.study.assessment.id}
            )

    @property
    def helper(self):
        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new experiment",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.instance.study.get_absolute_url(),
            }

        helper = BaseFormHelper(self, **inputs)
        helper.set_textarea_height()
        helper.add_row("name", 2, "col-md-6")
        helper.add_row("transfection", 2, "col-md-6")
        helper.add_row("dosing_notes", 2, "col-md-6")
        helper.add_row("has_positive_control", 2, "col-md-6")
        helper.add_row("has_negative_control", 2, "col-md-6")
        helper.add_row("has_vehicle_control", 2, "col-md-6")
        helper.add_row("control_notes", 2, "col-md-6")

        return helper


class CategoryModelChoice(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.choice_label


class OELWidget(Select):
    def set_default_choices(self, instance):
        choices = [
            (-999, "---"),
        ]

        if instance.id:
            for eg in instance.groups.all():
                choices.append((eg.dose_group_id, eg.dose))

        self.choices = choices


class IVEndpointForm(forms.ModelForm):
    HELP_TEXT_CREATE = ""
    HELP_TEXT_UPDATE = "Update an existing endpoint."

    category = CategoryModelChoice(
        required=False, queryset=models.IVEndpointCategory.objects.none()
    )
    assay_type = forms.CharField(
        label="Assay Type",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVEndpointAutocomplete, field="assay_type"
        ),
    )
    response_units = forms.CharField(
        label="Response Units",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVEndpointAutocomplete, field="response_units"
        ),
    )

    class Meta:
        model = models.IVEndpoint
        exclude = (
            "assessment",
            "experiment",
        )
        widgets = {
            "NOEL": OELWidget(),
            "LOEL": OELWidget(),
            "effects": AutocompleteSelectMultipleWidget(autocomplete_class=EffectTagAutocomplete),
        }

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop("parent", None)
        assessment = kwargs.pop("assessment", None)
        super().__init__(*args, **kwargs)
        if experiment:
            self.instance.experiment = experiment
        if assessment:
            self.instance.assessment = assessment

        self.fields["NOEL"].widget.set_default_choices(self.instance)
        self.fields["LOEL"].widget.set_default_choices(self.instance)

        self.fields["effect"].widget = AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVEndpointAutocomplete, field="effect"
        )

        self.fields["effects"].help_text = "Tags used to help categorize effect description."

        self.fields["chemical"].queryset = self.fields["chemical"].queryset.filter(
            study=self.instance.experiment.study
        )

        self.fields["category"].queryset = self.fields["category"].queryset.model.get_assessment_qs(
            self.instance.assessment_id
        )

        for field in ("assay_type", "response_units", "effect"):
            self.fields[field].widget.update_filters(
                {"experiment__study__assessment_id": self.instance.assessment_id}
            )

    def clean_additional_fields(self):
        data = self.cleaned_data["additional_fields"]
        try:
            json.loads(data)
        except ValueError:
            raise forms.ValidationError("Must be valid JSON.")
        return data

    @property
    def helper(self):
        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new endpoint",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.instance.experiment.get_absolute_url(),
            }

        helper = BaseFormHelper(self, **inputs)
        helper.set_textarea_height()
        helper.add_row("name", 2, "col-md-6")
        helper.add_row("chemical", 2, "col-md-6")
        helper.add_row("assay_type", 2, "col-md-6")
        helper.add_row("effect", 2, "col-md-6")
        helper.add_row("data_type", 4, "col-md-3")
        helper.add_row("observation_time", 4, "col-md-3")
        helper.add_row("monotonicity", 3, "col-md-4")
        helper.add_row("trend_test", 2, "col-md-6")
        helper.add_row("endpoint_notes", 2, "col-md-6")

        url = reverse("assessment:effect_tag_create", kwargs={"pk": self.instance.assessment_id})
        helper.add_create_btn("effects", url, "Add new effect tag")

        return helper


class IVEndpointGroupForm(forms.ModelForm):
    class Meta:
        model = models.IVEndpointGroup
        exclude = ("endpoint", "dose_group_id")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dose"].widget.attrs["class"] = "doses"


class BaseIVEndpointGroupFormset(BaseModelFormSet):
    pass


IVEndpointGroupFormset = modelformset_factory(
    models.IVEndpointGroup,
    form=IVEndpointGroupForm,
    formset=BaseIVEndpointGroupFormset,
    can_delete=True,
    extra=0,
)

BlankIVEndpointGroupFormset = modelformset_factory(
    models.IVEndpointGroup,
    form=IVEndpointGroupForm,
    formset=BaseIVEndpointGroupFormset,
    can_delete=True,
    extra=1,
)


class BaseIVBenchmarkForm(forms.ModelForm):
    class Meta:
        model = models.IVBenchmark
        fields = "__all__"


IVBenchmarkFormset = inlineformset_factory(
    models.IVEndpoint, models.IVBenchmark, form=BaseIVBenchmarkForm, extra=1
)
