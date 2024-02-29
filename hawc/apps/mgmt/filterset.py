import django_filters as df
from django.db.models import F, Q
from django.forms.widgets import CheckboxInput
from django_filters.constants import EMPTY_VALUES

from ..common.filterset import ArrowOrderingFilter, BaseFilterSet, InlineFilterForm
from ..myuser.models import HAWCUser
from ..study.constants import StudyTypeChoices
from . import constants, models


class TaskOrderingFilter(ArrowOrderingFilter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs.order_by("study_id", "type")
        ordering = [
            F("due_date").desc(nulls_last=True)
            if param == "-due_date"
            else self.get_ordering_value(param)
            for param in value
        ]
        ordering.extend(["study_id", "type"])
        return qs.order_by(*ordering)


class UserTaskFilterSet(BaseFilterSet):
    study_name = df.CharFilter(
        method="filter_search",
        label="Study",
        help_text="Filter by study name",
    )

    type = df.ChoiceFilter(
        empty_label="Task Type",
        choices=constants.TaskType.choices,
    )

    show_completed = df.BooleanFilter(
        method="filter_show_completed",
        label="Show completed and abandoned",
        initial=False,
        widget=CheckboxInput(),
    )

    class Meta:
        model = models.Task
        form = InlineFilterForm
        fields = ["study_name", "type", "show_completed"]
        main_field = "study_name"
        appended_fields = ["type", "show_completed"]

    def filter_show_completed(self, queryset, name, value):
        if value is True:
            return queryset
        return queryset.exclude_completed_and_abandonded()

    def filter_search(self, queryset, name, value):
        return queryset.filter(study__short_citation__icontains=value)


class TaskFilterSet(BaseFilterSet):
    study_name = df.CharFilter(
        lookup_expr="icontains",
        field_name="study__short_citation",
        label="Study name",
        help_text="Filter by study",
    )
    data_type = df.ChoiceFilter(
        method="filter_data_type",
        choices=StudyTypeChoices.choices,
        label="Data type",
        help_text="Data type for full-text extraction",
        empty_label="- Data Type -",
    )
    owner = df.ModelChoiceFilter(
        method="filter_owner",
        label="Assigned user",
        queryset=HAWCUser.objects.none(),
        help_text="Includes all tasks for a study where a user has at least one assignment",
        empty_label="- User -",
    )
    order_by = TaskOrderingFilter(
        label="Ordering",
        fields=(
            ("study__short_citation", "citation"),
            ("study__created", "study_created"),
            ("due_date", "due_date"),
        ),
        initial="citation",
    )

    class Meta:
        model = models.Task
        form = InlineFilterForm
        fields = ["study_name", "type", "status", "data_type", "owner", "order_by"]
        main_field = "study_name"
        appended_fields = ["data_type", "type", "owner", "status", "order_by"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_filters["status"].extra["empty_label"] = "- Status -"
        self.base_filters["type"].extra["empty_label"] = "- Type -"

    def filter_owner(self, queryset, name, value):
        return queryset.filter(
            study__in=queryset.filter(owner=value).values_list("study_id", flat=True)
        )

    def filter_search(self, queryset, name, value):
        query = Q(study__short_citation__icontains=value)
        return queryset.filter(query)

    def filter_data_type(self, queryset, name, value):
        return queryset.filter(**{f"study__{value}": True})

    def create_form(self):
        form = super().create_form()
        form.fields["owner"].queryset = self.assessment.pms_and_team_users()
        return form
