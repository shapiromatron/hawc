import django_filters as df
from django.db.models import Q

from ..common.autocomplete import AutocompleteTextWidget
from ..common.filterset import (
    BaseFilterSet,
    InlineFilterForm,
    PaginationFilter,
)
from . import autocomplete, models


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
            attrs={
                "data-placeholder": "Filter by name (ex: developmental)",
                "class": "autocompletefilter",
            },
        ),
    )
    design = df.CharFilter(
        lookup_expr="icontains",
        label="Experiment design",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.ExperimentAutocomplete,
            field="design",
            attrs={"data-placeholder": "Filter by design (ex: B)", "class": "autocompletefilter"},
        ),
    )
    chemical = df.CharFilter(
        field_name="v2_chemicals__name",
        lookup_expr="icontains",
        label="Chemical name",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.ChemicalAutocomplete,
            field="name",
            attrs={"data-placeholder": "Chemical name", "class": "autocompletefilter"},
        ),
        help_text="ex: sodium",
    )
    cas = df.CharFilter(
        field_name="v2_chemicals__cas",
        lookup_expr="icontains",
        label="CAS",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.ChemicalAutocomplete,
            field="cas",
            attrs={"data-placeholder": "CAS", "class": "autocompletefilter"},
        ),
        help_text="ex: 107-02-8",
    )
    paginate_by = PaginationFilter()

    class Meta:
        model = models.Experiment
        form = InlineFilterForm
        fields = ["query", "name", "design", "paginate_by"]
        main_field = "query"
        appended_fields = ["name", "design", "chemical", "cas", "paginate_by"]

    def __init__(self, *args, assessment, **kwargs):
        super().__init__(*args, assessment=assessment, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset).prefetch_related("v2_chemicals")
        queryset = queryset.filter(study__assessment=self.assessment, study__bioassay=True)
        return queryset

    def filter_query(self, queryset, name, value):
        query = Q(study__short_citation__icontains=value)
        return queryset.filter(query)
