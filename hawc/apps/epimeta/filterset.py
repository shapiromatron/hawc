import django_filters as df

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


class MetaResultFilterSet(BaseFilterSet):
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
            autocomplete_class=autocomplete.MetaResultAutocomplete,
            field="label",
            attrs={"data-placeholder": "Filter results (ex: folic acid, any time)"},
        ),
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
    order_by = OrderingFilter(
        fields=(
            ("protocol__study__short_citation", "study"),
            ("label", "meta_result"),
            ("protocol__name", "protocol"),
            ("health_outcome", "health_outcome"),
            ("estimate", "estimate"),
        ),
        choices=(
            ("study", "↑ study"),
            ("meta_result", "↑ meta result"),
            ("protocol", "↑ protocol"),
            ("health_outcome", "↑ health outcome"),
            ("estimate", "↑ estimate"),
        ),
        initial="study",
    )
    paginate_by = PaginationFilter()

    class Meta:
        model = models.MetaResult
        form = ExpandableFilterForm
        fields = [
            "studies",
            "label",
            "protocol",
            "health_outcome",
            "exposure_name",
            "order_by",
            "paginate_by",
        ]
        main_field = "label"
        appended_fields = ["order_by", "paginate_by"]
        grid_layout = {
            "rows": [
                {"columns": [{"width": 12}]},
                {"columns": [{"width": 3}, {"width": 3}, {"width": 3}, {"width": 3}]},
            ]
        }

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        queryset = queryset.filter(protocol__study__assessment=self.assessment)
        if not self.perms["edit"]:
            queryset = queryset.filter(protocol__study__published=True)
        return queryset

    def create_form(self):
        form = super().create_form()
        form.fields["studies"].set_filters({"assessment_id": self.assessment.id, "epi_meta": True})
        form.fields["protocol"].widget.update_filters({"study__assessment_id": self.assessment.id})
        for field in form.fields:
            widget = form.fields[field].widget
            if field in ("label", "health_outcome", "exposure_name"):
                widget.update_filters({"protocol__study__assessment_id": self.assessment.id})
        return form
