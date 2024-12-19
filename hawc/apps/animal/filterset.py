import django_filters as df
from django import forms
from django.db.models import Q

from ..assessment.autocomplete import EffectTagAutocomplete, SpeciesAutocomplete, StrainAutocomplete
from ..assessment.models import DoseUnits
from ..common.autocomplete import AutocompleteTextWidget
from ..common.filterset import (
    AutocompleteModelChoiceFilter,
    AutocompleteModelMultipleChoiceFilter,
    BaseFilterSet,
    ExpandableFilterForm,
    InlineFilterForm,
    OrderingFilter,
    PaginationFilter,
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
            autocomplete_class=autocomplete.EndpointAutocomplete,
            field="name",
            attrs={"data-placeholder": "Filter by endpoint name (ex: heart weight)"},
        ),
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
        distinct=True,
    )
    order_by = OrderingFilter(
        fields=(
            ("animal_group__experiment__study__short_citation", "study"),
            ("animal_group__experiment__name", "experiment_name"),
            ("animal_group__name", "animal_group"),
            ("name", "endpoint_name"),
            ("system", "system"),
            ("organ", "organ"),
            ("effect", "effect"),
            ("effect_subtype", "effect_subtype"),
            ("animal_group__experiment__chemical", "chemical"),
        ),
        choices=(
            ("study", "↑ study"),
            ("experiment_name", "↑ experiment name"),
            ("animal_group", "↑ animal group"),
            ("endpoint_name", "↑ endpoint name"),
            ("system", "↑ system"),
            ("organ", "↑ organ"),
            ("effect", "↑ effect"),
            ("effect_subtype", "↑ effect subtype"),
            ("chemical", "↑ chemical"),
        ),
        initial="study",
    )
    paginate_by = PaginationFilter()

    class Meta:
        model = models.Endpoint
        form = ExpandableFilterForm
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
        main_field = "name"
        appended_fields = ["order_by", "paginate_by"]
        grid_layout = {
            "rows": [
                {"columns": [{"width": 12}]},
                {"columns": [{"width": 3}, {"width": 3}, {"width": 3}, {"width": 3}]},
                {"columns": [{"width": 3}, {"width": 3}, {"width": 3}, {"width": 3}]},
                {"columns": [{"width": 3}, {"width": 3}, {"width": 3}, {"width": 3}]},
                {"columns": [{"width": 3}, {"width": 3}, {"width": 3}]},
            ]
        }

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


class ExperimentFilterSet(BaseFilterSet):
    query = df.CharFilter(
        method="filter_query",
        label="Short Citation",
        help_text="Filter citations (author, year, title, ID)",
    )
    name = df.CharFilter(
        lookup_expr="icontains",
        label="Experiment name",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.ExperimentAutocomplete,
            field="name",
            attrs={"data-placeholder": "Filter by name (ex: developmental)"},
        ),
    )
    type = df.CharFilter(
        lookup_expr="icontains",
        label="Experiment type",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.ExperimentAutocomplete,
            field="type",
            attrs={"data-placeholder": "Filter by type (ex: Dv)"},
        ),
    )
    chemical = df.CharFilter(
        field_name="chemical",
        lookup_expr="icontains",
        label="Chemical name",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.ExperimentAutocomplete,
            field="chemical",
            attrs={"data-placeholder": "Chemical name"},
        ),
        help_text="ex: sodium",
    )
    cas = df.CharFilter(
        field_name="cas",
        lookup_expr="icontains",
        label="CAS",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.ExperimentAutocomplete,
            field="cas",
            attrs={"data-placeholder": "CAS"},
        ),
        help_text="ex: 107-02-8",
    )
    paginate_by = PaginationFilter()

    class Meta:
        model = models.Experiment
        form = InlineFilterForm
        fields = ["query", "name", "type", "chemical", "cas", "paginate_by"]
        main_field = "query"
        appended_fields = ["name", "type", "chemical", "cas", "paginate_by"]

    def __init__(self, *args, assessment, **kwargs):
        super().__init__(*args, assessment=assessment, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        queryset = queryset.filter(study__assessment=self.assessment, study__bioassay=True)
        return queryset

    def filter_query(self, queryset, name, value):
        query = Q(study__short_citation__icontains=value)
        return queryset.filter(query)

    def create_form(self):
        form = super().create_form()
        if "assigned_user" in form.fields:
            form.fields["assigned_user"].queryset = self.assessment.pms_and_team_users()
        return form
