import django_filters as df

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
from . import autocomplete, models


class EndpointFilterSet(BaseFilterSet):
    studies = AutocompleteModelMultipleChoiceFilter(
        field_name="experiment__study",
        autocomplete_class=StudyAutocomplete,
        label="Study reference",
        help_text="ex: Smith et al. 2010",
    )
    name = df.CharFilter(
        lookup_expr="icontains",
        label="Endpoint name",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVEndpointAutocomplete,
            field="name",
            attrs={"data-placeholder": "Filter by endpoint name (ex: B cells)"},
        ),
    )
    chemical = df.CharFilter(
        field_name="chemical__name",
        lookup_expr="icontains",
        label="Chemical name",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVChemicalAutocomplete, field="name"
        ),
        help_text="ex: PFOA",
    )
    cas = df.CharFilter(
        field_name="chemical__cas",
        lookup_expr="icontains",
        label="CAS",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVChemicalAutocomplete, field="cas"
        ),
        help_text="ex: 107-02-8",
    )
    cell_type = df.CharFilter(
        field_name="experiment__cell_type__cell_type",
        lookup_expr="icontains",
        label="Cell type",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVCellTypeAutocomplete, field="cell_type"
        ),
        help_text="ex: HeLa",
    )
    tissue = df.CharFilter(
        field_name="experiment__cell_type__tissue",
        lookup_expr="icontains",
        label="Tissue",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVCellTypeAutocomplete, field="tissue"
        ),
        help_text="ex: adipocytes",
    )
    effect = df.CharFilter(
        lookup_expr="icontains",
        label="Effect",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVEndpointAutocomplete, field="effect"
        ),
        help_text="ex: gene expression",
    )
    response_units = df.CharFilter(
        lookup_expr="icontains",
        label="Response units",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.IVEndpointAutocomplete, field="response_units"
        ),
        help_text="ex: counts",
    )
    dose_units = df.ModelChoiceFilter(
        field_name="experiment__dose_units",
        label="Dose units",
        queryset=DoseUnits.objects.all(),
    )
    order_by = OrderingFilter(
        fields=(
            ("experiment__study__short_citation", "study"),
            ("experiment__name", "experiment_name"),
            ("name", "endpoint_name"),
            ("assay_type", "assay_type"),
            ("effect", "effect"),
            ("chemical__name", "chemical"),
            ("category__name", "category"),
            ("observation_time", "observation_time"),
        ),
        choices=(
            ("study", "↑ study"),
            ("experiment_name", "↑ experiment name"),
            ("endpoint_name", "↑ endpoint name"),
            ("assay_type", "↑ assay type"),
            ("effect", "↑ effect"),
            ("chemical", "↑ chemical"),
            ("category", "↑ category"),
            ("observation_time", "↑ observation time"),
        ),
        initial="study",
    )
    paginate_by = PaginationFilter()

    class Meta:
        model = models.IVEndpoint
        form = ExpandableFilterForm
        fields = [
            "studies",
            "name",
            "chemical",
            "cas",
            "cell_type",
            "tissue",
            "effect",
            "response_units",
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
            ]
        }

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        queryset = queryset.filter(assessment=self.assessment)
        if not self.perms["edit"]:
            queryset = queryset.filter(experiment__study__published=True)
        return queryset

    def create_form(self):
        form = super().create_form()
        form.fields["dose_units"].queryset = DoseUnits.objects.get_iv_units(self.assessment.id)
        form.fields["studies"].set_filters({"assessment_id": self.assessment.id, "in_vitro": True})
        # for endpoint autocomplete
        for field in ("name", "effect", "response_units"):
            form.fields[field].widget.update_filters(
                {"experiment__study__assessment_id": self.assessment.id}
            )
        # for chemical autocomplete
        for field in ("chemical", "cas"):
            form.fields[field].widget.update_filters({"study__assessment_id": self.assessment.id})
        # for cell type autocomplete
        for field in ("cell_type", "tissue"):
            form.fields[field].widget.update_filters({"study__assessment_id": self.assessment.id})
        return form
