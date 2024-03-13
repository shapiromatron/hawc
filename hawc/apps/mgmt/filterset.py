import django_filters as df
from django.db.models import F, Q
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
    type = df.ChoiceFilter(
        empty_label="- Type -",
        choices=constants.TaskType.choices,
    )
    owner = df.ModelChoiceFilter(
        label="Assigned user",
        queryset=HAWCUser.objects.none(),
        help_text="Includes all tasks for a study where a user has at least one assignment",
        empty_label="- User -",
    )
    status = df.ChoiceFilter(
        empty_label="- Status -",
        choices=constants.TaskStatus.extra_choices(),
        method="filter_status",
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

    def filter_search(self, queryset, name, value):
        query = Q(study__short_citation__icontains=value)
        return queryset.filter(query)

    def filter_data_type(self, queryset, name, value):
        return queryset.filter(**{f"study__{value}": True})

    def filter_status(self, queryset, name, value):
        return queryset.filter(constants.TaskStatus.filter_extra(int(value)))

    def create_form(self):
        form = super().create_form()
        form.fields["owner"].queryset = self.assessment.pms_and_team_users()
        return form
