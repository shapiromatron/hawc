import django_filters as df
from django_filters.constants import EMPTY_VALUES

from ..common.filterset import BaseFilterSet
from ..myuser.models import HAWCUser
from ..study.constants import StudyTypeChoices
from . import models


class TaskOrderingFilter(df.OrderingFilter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        ordering = [self.get_ordering_value(param) for param in value] + ["study_id", "type"]
        return qs.order_by(*ordering)


class TaskFilterSet(BaseFilterSet):
    study_name = df.CharFilter(
        lookup_expr="icontains", field_name="study__short_citation", label="Study name"
    )
    data_type = df.ChoiceFilter(
        method="filter_data_type",
        choices=StudyTypeChoices.filtered_choices(),
        label="Data type",
        help_text="Data type for full-text extraction",
        empty_label="<All>",
    )
    owner = df.ModelChoiceFilter(
        method="filter_owner",
        label="Assigned user",
        queryset=HAWCUser.objects.none(),
        help_text="Includes all tasks for a study where a user has at least one assignment",
        empty_label="<All>",
    )
    order_by = TaskOrderingFilter(
        label="Ordering",
        fields=(("study__short_citation", "study_name"), ("study__created", "study_created")),
        empty_label=None,
        null_label=None,
    )

    class Meta:
        model = models.Task
        fields = ["study_name", "data_type", "owner", "order_by"]
        grid_layout = {
            "rows": [
                {"columns": [{"width": 3}, {"width": 3}, {"width": 3}, {"width": 3}]},
            ]
        }

    def filter_owner(self, queryset, name, value):
        return queryset.filter(
            study__in=queryset.filter(owner=value).values_list("study_id", flat=True)
        )

    def filter_data_type(self, queryset, name, value):
        return queryset.filter(**{f"study__{value}": True})

    def create_form(self):
        form = super().create_form()
        form.fields["owner"].queryset = self.assessment.pms_and_team_users()
        return form
