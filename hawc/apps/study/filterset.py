import django_filters as df
from django.db.models import Q

from ..common.filterset import BaseFilterSet, InlineFilterForm
from ..myuser.models import HAWCUser
from . import constants, models


class StudyFilterSet(BaseFilterSet):
    query = df.CharFilter(
        method="filter_query",
        label="Citation",
        help_text="Filter citations (author, year, title, ID)",
    )
    data_type = df.ChoiceFilter(
        method="filter_data_type",
        choices=constants.StudyTypeChoices.filtered_choices(),
        label="Data type",
        help_text="Data type for full-text extraction",
        empty_label="All data types",
    )
    published = df.ChoiceFilter(
        choices=[(True, "Published only"), (False, "Unpublished only")],
        label="Published",
        help_text="Published status for HAWC study",
        empty_label="Published status",
    )
    assigned_user = df.ModelChoiceFilter(
        method="filter_assigned_user",
        queryset=HAWCUser.objects.all(),
        label="Assigned user",
        help_text="A user with active study evaluation assignments",
        empty_label="All users",
    )

    class Meta:
        model = models.Study
        form = InlineFilterForm
        fields = ["query", "data_type", "published", "assigned_user"]
        main_field = "query"
        appended_fields = ["data_type", "assigned_user", "published"]

    def __init__(self, *args, assessment, **kwargs):
        super().__init__(*args, assessment=assessment, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        query = Q(assessment=self.assessment)
        if not self.perms["edit"]:
            query &= Q(published=True)
        return queryset.filter(query)

    def filter_query(self, queryset, name, value):
        query = (
            Q(short_citation__icontains=value)
            | Q(full_citation__icontains=value)
            | Q(identifiers__unique_id__icontains=value)
        )
        return queryset.filter(query)

    def filter_data_type(self, queryset, name, value):
        return queryset.filter(**{value: True})

    def filter_assigned_user(self, queryset, name, value):
        return queryset.filter(riskofbiases__author=value, riskofbiases__active=True).distinct()

    def create_form(self):
        form = super().create_form()
        if "assigned_user" in form.fields:
            form.fields["assigned_user"].queryset = self.assessment.pms_and_team_users()
        return form
