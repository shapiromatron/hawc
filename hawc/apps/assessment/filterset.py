import django_filters as df
from django.db.models import Q

from ..common.filterset import ArrowOrderingFilter, BaseFilterSet, InlineFilterForm
from . import models
from .constants import PublishedStatus


class AssessmentFilterSet(BaseFilterSet):
    search = df.CharFilter(
        method="filter_search",
        label="Search",
        help_text="Search by name, year, chemical, or project type",
    )
    role = df.ChoiceFilter(
        empty_label="Role",
        method="filter_role",
        choices=[
            ("project_manager", "Project Manager"),
            ("team_members", "Team Member"),
            ("reviewers", "Reviewer"),
        ],
        label="Role",
        help_text="Filter by your role for an assessment.",
    )
    published_status = df.ChoiceFilter(
        empty_label="Published Status",
        method="filter_published",
        choices=PublishedStatus.choices,
        label="Published",
        help_text="Published status of assessment.",
    )
    order_by = ArrowOrderingFilter(
        fields=(
            ("name", "name"),
            ("year", "year"),
            ("last_updated", "Date Updated"),
        ),
        initial="-year",
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

    def filter_published(self, queryset, name, value):
        return queryset.with_published().filter(published=value)


class GlobalChemicalsFilterSet(df.FilterSet):
    query = df.CharFilter(
        method="filter_query",
        label="Query",
        help_text="Enter chemical name, DTXSID, or CASRN",
    )
    public_only = df.BooleanFilter(method="filter_public_only")  # public_only=true/false

    def filter_query(self, queryset, name, value):
        query = (
            Q(name__icontains=value)
            | Q(cas=value)
            | Q(dtxsids__dtxsid=value)
            | Q(dtxsids__content__preferredName__icontains=value)
            | Q(dtxsids__content__casrn=value)
        )
        return queryset.filter(query).distinct()

    def filter_public_only(self, queryset, name, value):
        if value is True:
            return queryset.filter(public_on__isnull=False, hide_from_public_page=False)
        return queryset
