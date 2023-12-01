import django_filters as df
from django import forms
from django.db.models import Q
from django.urls import reverse

from ..common.filterset import (
    ArrowOrderingFilter,
    BaseFilterSet,
    ExpandableFilterForm,
    InlineFilterForm,
    OrderingFilter,
    PaginationFilter,
)
from ..common.helper import new_window_a
from ..myuser.models import HAWCUser
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
        return queryset.filter(query)

    def filter_role(self, queryset, name, value):
        return queryset.filter(**{value: self.request.user})

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


class LogFilterSet(BaseFilterSet):
    user = df.ModelChoiceFilter(
        label="User",
        queryset=HAWCUser.objects.all(),
        help_text="The user who made the change",
        empty_label="All Users",
    )
    object_id = df.NumberFilter(
        label="Object ID",
        help_text="Filter by HAWC ID; can be found in the URL or in data exports",
    )
    content_type = df.NumberFilter(
        label="Data type",
    )
    before = df.DateFilter(
        label="Modified before",
        widget=forms.widgets.DateInput(attrs={"type": "date"}),
        method="filter_before",
    )
    after = df.DateFilter(
        label="Modified After",
        widget=forms.widgets.DateInput(attrs={"type": "date"}),
        method="filter_after",
    )
    on = df.DateFilter(
        label="Modified On",
        widget=forms.widgets.DateInput(attrs={"type": "date"}),
        method="filter_on",
    )

    class Meta:
        model = models.Log
        form = ExpandableFilterForm
        fields = ("user", "object_id", "content_type", "before", "after", "on")
        main_field = "object_id"
        appended_fields = ("user",)
        grid_layout = {
            "rows": [
                {"columns": [{"width": 12}]},
                {"columns": [{"width": 3}, {"width": 3}, {"width": 3}, {"width": 3}]},
            ]
        }

    def filter_before(self, queryset, name, value):
        query = Q(created__date__lt=value)
        return queryset.filter(query)

    def filter_after(self, queryset, name, value):
        query = Q(created__date__gt=value)
        return queryset.filter(query)

    def filter_on(self, queryset, name, value):
        query = Q(created__date=value)
        return queryset.filter(query)

    def create_form(self):
        form = super().create_form()
        url = reverse("assessment:content_types")
        form.fields[
            "content_type"
        ].help_text = f"""Data {new_window_a(url, "content type")}; by filtering by data types below the content type can also be set."""
        form.fields["user"].queryset = self.assessment.pms_and_team_users()
        return form


class EffectTagFilterSet(df.FilterSet):
    name = df.CharFilter(lookup_expr="icontains")


class AssessmentValueFilterSet(df.FilterSet):
    name = df.CharFilter(
        field_name="assessment__name",
        lookup_expr="icontains",
        label="Assessment name",
    )
    cas = df.CharFilter(
        field_name="assessment__cas",
        label="Assessment CAS",
    )
    project_type = df.CharFilter(
        field_name="assessment__details__project_type",
        lookup_expr="icontains",
        label="Assessment project type",
    )
    year = df.CharFilter(field_name="assessment__year", label="Assessment year")

    order_by = OrderingFilter(
        fields=(
            (
                "assessment__name",
                "name",
            ),
            ("assessment__id", "assessment_id"),
        ),
        initial="name",
    )

    paginate_by = PaginationFilter()

    class Meta:
        model = models.AssessmentValue
        fields = ["value_type"]
