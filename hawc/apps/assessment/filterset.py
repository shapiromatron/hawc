import django_filters as df
from django import forms
from django.db.models import Q, TextField
from django.db.models.functions import Concat
from django.urls import reverse

from ..common.filterset import (
    ArrowOrderingFilter,
    AutocompleteModelMultipleChoiceFilter,
    BaseFilterSet,
    ExpandableFilterForm,
    InlineFilterForm,
)
from ..common.helper import new_window_a
from ..myuser.models import HAWCUser
from . import models
from .autocomplete import LabelAutocomplete
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


class LabeledItemFilterset(BaseFilterSet):
    name = df.CharFilter(
        method="filter_title",
        label="Object Name",
        help_text="Filter by object name",
    )
    label = AutocompleteModelMultipleChoiceFilter(
        autocomplete_class=LabelAutocomplete,
        method="filter_labels",
    )

    class Meta:
        model = models.LabeledItem
        form = InlineFilterForm
        fields = ("name", "label")

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.filter(label__assessment=self.assessment)

    def filter_title(self, queryset, name, value):
        if not value:
            return queryset
        query = (
            Q(summary_table__title__icontains=value)
            | Q(visual__title__icontains=value)
            | Q(datapivot_query__title__icontains=value)
            | Q(datapivot_upload__title__icontains=value)
        )
        return queryset.filter(query)

    def filter_labels(self, queryset, name, value):
        if not value:
            return queryset
        queryset = queryset.annotate(
            object_info=Concat("content_type", "object_id", output_field=TextField()),
        )  # annotate each in the list with content_type + object_id to create a unique field
        matching_objects = None
        for label in value:
            if (
                not matching_objects or len(matching_objects) > 0
            ):  # quit early if we run out of matching objects
                objects_with_label = (
                    queryset.filter(
                        label__path__startswith=label.path, label__depth__gte=label.depth
                    )
                    .values_list("object_info", flat=True)
                    .distinct()
                )
                matching_objects = (
                    matching_objects.intersection(objects_with_label)
                    if matching_objects
                    else set(objects_with_label)
                )  # only filtering for objects matching all labels
        return queryset.filter(object_info__in=matching_objects)

    def create_form(self):
        form = super().create_form()
        form.fields["label"].set_filters({"assessment_id": self.assessment.id})
        form.fields["label"].widget.attrs.update({"data-placeholder": "Filter by labels"})
        form.fields["label"].widget.attrs["size"] = 1
        return form
