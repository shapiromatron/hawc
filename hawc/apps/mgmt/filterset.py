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
    type = df.ModelChoiceFilter(
        queryset=models.TaskType.objects.none(),
        method="filter_type",
        empty_label="- Type -",
    )
    owner = df.ModelChoiceFilter(
        label="Assigned user",
        queryset=HAWCUser.objects.none(),
        help_text="Includes all tasks for a study where a user has at least one assignment",
        empty_label="- User -",
    )
    # The status search filter is now dynamic. To continue displaying the 'active' and 'inactive'
    # search options, it can't use the ModelChoiceFilter that 'type' now uses.
    status = df.ChoiceFilter(
        empty_label="- Status -",
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

    def filter_type(self, queryset, name, value):
        return queryset.filter(type=value)

    def filter_status(self, queryset, name, value):
        return queryset.filter(constants.TaskStatus.filter_extra(int(value)))

    def get_status_choices(self, assessment):
        model_choices = models.TaskStatus.objects.filter(assessment=assessment).values_list(
            "id", "name"
        )
        extra_choices = constants.TaskStatus.extra_choices()
        return list(model_choices) + extra_choices

    def create_form(self):
        self.filters["status"].extra.update({"choices": self.get_status_choices(self.assessment)})

        form = super().create_form()
        form.fields["type"].queryset = models.TaskType.objects.filter(assessment=self.assessment)
        form.fields["owner"].queryset = self.assessment.pms_and_team_users()
        return form
