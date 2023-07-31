import django_filters as df
from django import forms
from django.db.models import Q

from ..assessment.models import DoseUnits
from ..common.autocomplete import AutocompleteTextWidget
from ..common.filterset import (
    AutocompleteModelMultipleChoiceFilter,
    BaseFilterSet,
    ExpandableFilterForm,
    OrderingFilter,
    PaginationFilter,
)
from ..study.autocomplete import StudyAutocomplete
from . import autocomplete, constants, models


class OutcomeFilterSet(BaseFilterSet):
    studies = AutocompleteModelMultipleChoiceFilter(
        field_name="study_population__study",
        autocomplete_class=StudyAutocomplete,
        label="Study reference",
        help_text="ex: Smith et al. 2010",
    )
    name = df.CharFilter(
        lookup_expr="icontains",
        label="Outcome name",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.OutcomeAutocomplete,
            field="name",
            attrs={"data-placeholder": "Filter by endpoint name (ex: blood, glucose)"},
        ),
    )
    study_population = df.CharFilter(
        field_name="study_population__name",
        lookup_expr="icontains",
        label="Study population",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.StudyPopulationAutocomplete, field="name"
        ),
        help_text="ex: population near a Teflon manufacturing plant",
    )
    metric = df.CharFilter(
        field_name="study_population__exposures__metric",
        lookup_expr="icontains",
        label="Measurement metric",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.ExposureAutocomplete, field="metric"
        ),
        help_text="ex: drinking water",
    )
    age_profile = df.CharFilter(
        field_name="study_population__age_profile",
        lookup_expr="icontains",
        label="Age profile",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.StudyPopulationAutocomplete, field="age_profile"
        ),
        help_text="ex: children",
    )
    source = df.CharFilter(
        field_name="study_population__source",
        lookup_expr="icontains",
        label="Study population source",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.StudyPopulationAutocomplete, field="source"
        ),
        help_text="ex: occupational exposure",
    )
    country = df.CharFilter(
        field_name="study_population__countries__name",
        lookup_expr="icontains",
        label="Study population country",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.CountryAutocomplete, field="name"
        ),
        help_text="ex: Japan",
    )
    design = df.MultipleChoiceFilter(
        field_name="study_population__design",
        label="Study design",
        choices=constants.Design.choices,
        widget=forms.CheckboxSelectMultiple,
        initial=constants.Design.values,
    )
    system = df.CharFilter(
        lookup_expr="icontains",
        label="System",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.OutcomeAutocomplete, field="system"
        ),
        help_text="ex: immune and lymphatic system",
    )
    effect = df.CharFilter(
        lookup_expr="icontains",
        label="Effect",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.OutcomeAutocomplete, field="effect"
        ),
        help_text="ex: Cancer",
    )
    effect_subtype = df.CharFilter(
        lookup_expr="icontains",
        label="Effect subtype",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.OutcomeAutocomplete, field="effect_subtype"
        ),
        help_text="ex: Melanoma",
    )
    diagnostic = df.MultipleChoiceFilter(
        field_name="diagnostic",
        choices=constants.Diagnostic.choices,
        widget=forms.CheckboxSelectMultiple,
        initial=constants.Diagnostic.values,
    )
    metric_units = df.ModelChoiceFilter(
        field_name="study_population__exposures__metric_units",
        label="Metric units",
        queryset=DoseUnits.objects.all(),
    )
    order_by = OrderingFilter(
        fields=(
            ("study_population__study__short_citation", "study"),
            ("study_population__name", "study_population"),
            ("name", "outcome_name"),
            ("system", "system"),
            ("effect", "effect"),
            ("diagnostic", "diagnostic"),
        ),
        choices=(
            ("study", "↑ study"),
            ("study_population", "↑ study population"),
            ("outcome_name", "↑ outcome name"),
            ("system", "↑ system"),
            ("effect", "↑ effect"),
            ("diagnostic", "↑ diagnostic"),
        ),
        initial="study",
    )
    paginate_by = PaginationFilter()

    class Meta:
        model = models.Outcome
        form = ExpandableFilterForm
        fields = [
            "studies",
            "name",
            "study_population",
            "metric",
            "age_profile",
            "source",
            "country",
            "system",
            "design",
            "effect",
            "effect_subtype",
            "metric_units",
            "diagnostic",
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
            ]
        }

    def filter_search(self, queryset, name, value):
        query = Q(name__icontains=value)
        return queryset.filter(query)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        queryset = queryset.filter(assessment=self.assessment)
        if not self.perms["edit"]:
            queryset = queryset.filter(study_population__study__published=True)
        return queryset

    def create_form(self):
        form = super().create_form()
        form.fields["studies"].set_filters({"assessment_id": self.assessment.id, "epi": True})
        form.fields["metric"].widget.update_filters(
            {"study_population__study__assessment_id": self.assessment.id}
        )
        form.fields["country"].widget.update_filters(
            {"studypopulation__study__assessment_id": self.assessment.id}
        )
        form.fields["metric_units"].queryset = DoseUnits.objects.get_epi_units(self.assessment.id)
        for field in form.fields:
            widget = form.fields[field].widget
            # for study population autocomplete
            if field in ("study_population", "age_profile", "source"):
                widget.update_filters({"study__assessment_id": self.assessment.id})
            # for outcome autocomplete
            elif field in ("name", "system", "effect", "effect_subtype"):
                widget.update_filters(
                    {"study_population__study__assessment_id": self.assessment.id}
                )
        return form
