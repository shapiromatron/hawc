import django_filters as df
from django.db.models import Q

from ..common.filterset import BaseFilterSet, InlineFilterForm
from . import models


class AssessmentFilterset(BaseFilterSet):
    search = df.CharFilter(
        method="filter_search",
        label="Search",
        help_text="Search by name, year, chemical, or project type",
    )
    role = df.ChoiceFilter(
        empty_label="Filter by role",
        method="filter_role",
        choices=[
            ("project_manager", "Project Manager"),
            ("team_members", "Team Member"),
            ("reviewers", "Reviewer"),
        ],
        label="Role",
        help_text="Filter by your role for an assessment.",
    )
    order_by = df.OrderingFilter(
        fields=(
            ("name", "name"),
            ("year", "year"),
            ("last_updated", "Date Updated"),
        ),
        initial="-year",
        empty_label=None,
        help_text="How results will be ordered",
    )

    class Meta:
        model = models.Assessment
        form = InlineFilterForm
        fields = ("search", "role", "order_by")

    def filter_search(self, queryset, name, value):
        query = (
            Q(name__icontains=value)
            | Q(year__icontains=value)
            | Q(authors__unaccent__icontains=value)
            | Q(cas__icontains=value)
            | Q(dtxsids__dtxsid__icontains=value)
            | Q(dtxsids__content__casrn=value)
            | Q(dtxsids__content__preferredName__icontains=value)
            | Q(details__project_type__icontains=value)
            | Q(details__report_id__icontains=value)
        )
        return queryset.filter(query).distinct()

    def filter_role(self, queryset, name, value):
        return queryset.filter(**{value: self.request.user}).distinct()
