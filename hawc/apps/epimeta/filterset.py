import django_filters as df
from django.db.models import Q

from ..common.autocomplete import AutocompleteTextWidget
from ..common.filterset import (
    AutocompleteModelMultipleChoiceFilter,
    BaseFilterSet,
    ExpandableFilterForm,
    PaginationFilter,
)
from ..study.autocomplete import StudyAutocomplete
from . import autocomplete, models


class MetaResultFilterSet(BaseFilterSet):
    search = df.CharFilter(
        method="filter_search", label="Health outcomes", help_text="Filter by health outcome"
    )
    studies = AutocompleteModelMultipleChoiceFilter(
        field_name="protocol__study",
        autocomplete_class=StudyAutocomplete,
        label="Study reference",
        help_text="ex: Smith et al. 2010",
    )
    label = df.CharFilter(
        lookup_expr="icontains",
        label="Meta result label",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.MetaResultAutocomplete, field="label"
        ),
        help_text="ex: ALL, folic acid, any time",
    )
    protocol = df.CharFilter(
        field_name="protocol__name",
        lookup_expr="icontains",
        label="Protocol",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.MetaProtocolAutocomplete, field="name"
        ),
        help_text="ex: B vitamins and risk of cancer",
    )
    health_outcome = df.CharFilter(
        lookup_expr="icontains",
        label="Health outcome",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.MetaResultAutocomplete, field="health_outcome"
        ),
        help_text="ex: Any adenoma",
    )
    exposure_name = df.CharFilter(
        lookup_expr="icontains",
        label="Exposure name",
        widget=AutocompleteTextWidget(
            autocomplete_class=autocomplete.MetaResultAutocomplete, field="exposure_name"
        ),
        help_text="ex: Folate",
    )
    order_by = df.OrderingFilter(
        fields=(
            ("protocol__study__short_citation", "study"),
            ("label", "meta result label"),
            ("protocol__name", "protocol"),
            ("health_outcome", "health outcome"),
            ("estimate", "estimate"),
        ),
        choices=(
            ("study", "study"),
            ("meta result label", "meta result label"),
            ("protocol", "protocol"),
            ("health outcome", "health outcome"),
            ("estimate", "estimate"),
        ),
        empty_label=("Default Order"),
    )
    paginate_by = PaginationFilter(empty_label="Default Pagination")

    class Meta:
        model = models.MetaResult
        form = ExpandableFilterForm
        fields = [
            "search",
            "studies",
            "label",
            "protocol",
            "health_outcome",
            "exposure_name",
            "order_by",
            "paginate_by",
        ]
        grid_layout = {
            "rows": [
                {"columns": [{"width": 12}]},
                {"columns": [{"width": 3}, {"width": 3}, {"width": 3}, {"width": 3}]},
                {"columns": [{"width": 3}]},
            ]
        }

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        queryset = queryset.filter(protocol__study__assessment=self.assessment)
        if not self.perms["edit"]:
            queryset = queryset.filter(protocol__study__published=True)
        return queryset

    def filter_search(self, queryset, name, value):
        query = Q(health_outcome__icontains=value)
        return queryset.filter(query)

    def create_form(self):
        form = super().create_form()
        form.fields["studies"].set_filters({"assessment_id": self.assessment.id, "epi_meta": True})
        form.fields["protocol"].widget.update_filters({"study__assessment_id": self.assessment.id})
        for field in form.fields:
            widget = form.fields[field].widget
            if field in ("label", "health_outcome", "exposure_name"):
                widget.update_filters({"protocol__study__assessment_id": self.assessment.id})
        return form
