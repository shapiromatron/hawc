import django_filters as df

from ..common.filterset import (
    ArrowOrderingFilter,
    AutocompleteModelMultipleChoiceFilter,
    BaseFilterSet,
    ExpandableFilterForm,
    PaginationFilter,
)
from ..study.autocomplete import StudyAutocomplete
from . import constants, models


class OutcomeFilterSet(BaseFilterSet):
    name = df.CharFilter(
        field_name="endpoint",
        lookup_expr="icontains",
        label="Endpoint",
        help_text="Filter by outcome name (ex: B vitamins and risk of cancer)",
    )
    studies = AutocompleteModelMultipleChoiceFilter(
        field_name="design__study",
        autocomplete_class=StudyAutocomplete,
        label="Study reference",
        help_text="ex: Smith et al. 2010",
    )
    design = df.MultipleChoiceFilter(
        field_name="design__study_design",
        label="Study Design",
        choices=constants.StudyDesign.choices,
    )
    order_by = ArrowOrderingFilter(
        fields=(
            ("design__study__short_citation", "study"),
            ("endpoint", "endpoint"),
        ),
        initial="study",
        empty_label=None,
    )
    paginate_by = PaginationFilter()

    class Meta:
        model = models.Outcome
        form = ExpandableFilterForm
        fields = [
            "name",
            "order_by",
            "paginate_by",
            "studies",
            "design",
            "system",
        ]
        main_field = "name"
        appended_fields = ["order_by", "paginate_by"]
        grid_layout = {
            "rows": [
                {"columns": [{"width": 12}]},
                {"columns": [{"width": 4}, {"width": 4}, {"width": 4}]},
            ]
        }

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        queryset = queryset.filter(design__study__assessment=self.assessment)
        if not self.perms["edit"]:
            queryset = queryset.filter(design__study__published=True)
        queryset = queryset.select_related("design__study")
        return queryset

    def create_form(self):
        form = super().create_form()
        form.fields["studies"].set_filters({"assessment_id": self.assessment.id, "epi": True})
        return form
