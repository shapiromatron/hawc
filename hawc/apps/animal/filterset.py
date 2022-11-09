import django_filters as df
from django import forms

from ..assessment.autocomplete import EffectTagAutocomplete, SpeciesAutocomplete, StrainAutocomplete
from ..assessment.models import DoseUnits
from ..common.autocomplete import AutocompleteTextWidget
from ..common.filterset import (
    AutocompleteModelChoiceFilter,
    AutocompleteModelMultipleChoiceFilter,
    BaseFilterSet,
)
from ..study.autocomplete import StudyAutocomplete
from . import autocomplete, constants, models


class EndpointFilterSet(BaseFilterSet):
    studies = AutocompleteModelMultipleChoiceFilter(
        field_name="animal_group__experiment__study",
        autocomplete_class=StudyAutocomplete,
        label="Study reference",
        help_text="ex: Smith et al. 2010",
    )
    chemical = df.CharFilter(
        field_name="animal_group__experiment__chemical",
        lookup_expr="icontains",
        label="Chemical name",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.ExperimentAutocomplete, field="chemical"
        ),
        help_text="ex: sodium",
    )
    cas = df.CharFilter(
        field_name="animal_group__experiment__cas",
        lookup_expr="icontains",
        label="CAS",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.ExperimentAutocomplete, field="cas"
        ),
        help_text="ex: 107-02-8",
    )
    lifestage_exposed = df.CharFilter(
        field_name="animal_group__lifestage_exposed",
        lookup_expr="icontains",
        label="Lifestage exposed",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.AnimalGroupAutocomplete, field="lifestage_exposed"
        ),
        help_text="ex: pup",
    )
    lifestage_assessed = df.CharFilter(
        field_name="animal_group__lifestage_assessed",
        lookup_expr="icontains",
        label="Lifestage assessed",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.AnimalGroupAutocomplete, field="lifestage_assessed"
        ),
        help_text="ex: adult",
    )
    species = AutocompleteModelChoiceFilter(
        field_name="animal_group__species",
        autocomplete_class=SpeciesAutocomplete,
        label="Species",
        help_text="ex: Mouse",
    )
    strain = AutocompleteModelChoiceFilter(
        field_name="animal_group__strain",
        autocomplete_class=StrainAutocomplete,
        label="Strain",
        help_text="ex: B6C3F1",
    )
    sex = df.MultipleChoiceFilter(
        field_name="animal_group__sex",
        label="Sex",
        choices=constants.Sex.choices,
        widget=forms.CheckboxSelectMultiple,
        initial=constants.Sex.values,
    )
    data_extracted = df.ChoiceFilter(
        choices=(
            (True, "Yes"),
            (False, "No"),
        ),
        empty_label="All data",
    )
    name = df.CharFilter(
        lookup_expr="icontains",
        label="Endpoint name",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.EndpointAutocomplete, field="name"
        ),
        help_text="ex: heart weight",
    )
    system = df.CharFilter(
        lookup_expr="icontains",
        label="System",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.EndpointAutocomplete, field="system"
        ),
        help_text="ex: endocrine",
    )
    organ = df.CharFilter(
        lookup_expr="icontains",
        label="Organ",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.EndpointAutocomplete, field="organ"
        ),
        help_text="ex: pituitary",
    )
    effect = df.CharFilter(
        lookup_expr="icontains",
        label="Effect",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.EndpointAutocomplete, field="effect"
        ),
        help_text="ex: alanine aminotransferase (ALT)",
    )
    effect_subtype = df.CharFilter(
        lookup_expr="icontains",
        label="Effect Subtype",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.EndpointAutocomplete, field="effect_subtype"
        ),
        help_text="ex: ",
    )
    tags = df.CharFilter(
        field_name="effects__name",
        lookup_expr="icontains",
        label="Tags",
        widget=AutocompleteTextWidget(autocomplete_class=EffectTagAutocomplete, field="name"),
        help_text="ex: antibody response",
    )
    dose_units = df.ModelChoiceFilter(
        field_name="animal_group__dosing_regime__doses__dose_units",
        label="Dose units",
        queryset=DoseUnits.objects.all(),
    )
    order_by = df.OrderingFilter(
        fields=(
            ("animal_group__experiment__study__short_citation", "study"),
            ("animal_group__experiment__name", "experiment name"),
            ("animal_group__name", "animal group"),
            ("name", "endpoint name"),
            ("animal_group__dosing_regime__doses__dose_units_id", "dose units"),
            ("system", "system"),
            ("organ", "organ"),
            ("effect", "effect"),
            ("effect_subtype", "effect subtype"),
            ("animal_group__experiment__chemical", "chemical"),
        ),
        choices=(
            ("study", "study"),
            ("experiment name", "experiment name"),
            ("animal group", "animal group"),
            ("endpoint name", "endpoint name"),
            ("dose units", "dose units"),
            ("system", "system"),
            ("organ", "organ"),
            ("effect", "effect"),
            ("effect subtype", "effect subtype"),
            ("chemical", "chemical"),
        ),
    )

    class Meta:
        model = models.Endpoint
        fields = [
            "studies",
            "chemical",
            "cas",
            "lifestage_exposed",
            "lifestage_assessed",
            "species",
            "strain",
            "sex",
            "data_extracted",
            "name",
            "system",
            "organ",
            "effect",
            "effect_subtype",
            "tags",
            "dose_units",
            "order_by",
            "paginate_by",
        ]
        grid_layout = [
            [3, 3, 3, 3],
            [3, 3, 3, 3],
            [3, 3, 3, 3],
            [3, 3, 3, 3],
            [3, 3],
        ]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        queryset = queryset.filter(assessment=self.assessment)
        if not self.perms["edit"]:
            queryset = queryset.filter(animal_group__experiment__study__published=True)
        return queryset

    def create_form(self):
        form = super().create_form()
        form.fields["studies"].set_filters({"assessment_id": self.assessment.id, "bioassay": True})
        form.fields["species"].set_filters(
            {"animalgroup__experiment__study__assessment_id": self.assessment.id}
        )
        form.fields["strain"].set_filters(
            {"animalgroup__experiment__study__assessment_id": self.assessment.id}
        )

        for field in form.fields:
            widget = form.fields[field].widget
            if field in ("chemical", "cas"):
                widget.update_filters({"study__assessment_id": self.assessment.id})
            elif field in ("lifestage_exposed", "lifestage_assessed"):
                widget.update_filters({"experiment__study__assessment_id": self.assessment.id})
            elif field in ("name", "system", "organ", "effect", "effect_subtype"):
                widget.update_filters(
                    {"animal_group__experiment__study__assessment_id": self.assessment.id}
                )

        form.fields["dose_units"].queryset = DoseUnits.objects.get_animal_units(self.assessment.id)
        return form
