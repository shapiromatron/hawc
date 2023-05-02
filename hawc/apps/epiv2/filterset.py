from ..common.filterset import (
    AutocompleteModelMultipleChoiceFilter,
    BaseFilterSet,
    PaginationFilter,
)
from ..study.autocomplete import StudyAutocomplete
from . import models


class OutcomeFilterSet(BaseFilterSet):
    studies = AutocompleteModelMultipleChoiceFilter(
        field_name="design__study",
        autocomplete_class=StudyAutocomplete,
        label="Study reference",
        help_text="ex: Smith et al. 2010",
    )
    paginate_by = PaginationFilter()

    class Meta:
        model = models.Outcome
        fields = [
            "studies",
            "paginate_by",
        ]
        grid_layout = {
            "rows": [
                {"columns": [{"width": 3}, {"width": 3}]},
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
