import django_filters as df
from django.db.models import Q

from ..common.filterset import BaseFilterSet
from . import models


class StudyFilterSet(BaseFilterSet):
    citation = df.CharFilter(
        method="filter_citation", label="Citation", help_text="Authors, year, title, etc."
    )
    identifier = df.CharFilter(
        field_name="identifiers__unique_id",
        lookup_expr="icontains",
        label="Identifier",
        help_text="Database identifier<br/>(PubMed ID, DOI, HERO ID, etc)",
    )
    data_type = df.ChoiceFilter(
        method="filter_data_type",
        choices=[
            ("bioassay", "Bioassay"),
            ("epi", "Epidemiology"),
            ("epi_meta", "Epidemiology meta-analysis"),
            ("in_vitro", "In vitro"),
        ],
        label="Data type",
        help_text="Data type for full-text extraction",
        empty_label="<All>",
    )
    published = df.ChoiceFilter(
        choices=[(True, "Published only"), (False, "Unpublished only")],
        label="Published",
        help_text="Published status for HAWC extraction",
        empty_label="<All>",
    )

    class Meta:
        model = models.Study
        fields = [
            "citation",
            "identifier",
            "data_type",
            "published",
        ]
        grid_layout = {
            "rows": [
                {"columns": [{"width": 3}, {"width": 3}, {"width": 3}, {"width": 3}]},
            ]
        }

    def filter_citation(self, queryset, name, value):
        query = Q(short_citation__icontains=value) | Q(full_citation__icontains=value)
        return queryset.filter(query)

    def filter_data_type(self, queryset, name, value):
        return queryset.filter(**{value: True})

    def prefilter_queryset(self, queryset):
        query = Q(assessment=self.assessment)
        if not self.perms["edit"]:
            query &= Q(published=True)
        return queryset.filter(query)

    def change_form(self, form):
        if not self.perms["edit"]:
            form.fields.pop("published")
            form.grid_layout.rows[0].columns.pop()
        return form
