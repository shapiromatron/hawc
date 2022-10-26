import django_filters as df
from django.db.models import Q

from ..common.filterset import BaseFilterSet, PaginationFilter
from . import models


class ReferenceFilterSet(BaseFilterSet):
    id = df.NumberFilter(label="HAWC ID", help_text="HAWC reference ID.")
    db_id = df.CharFilter(
        field_name="identifiers__unique_id",
        lookup_expr="icontains",
        label="External identifier",
        help_text="Pubmed ID, DOI, HERO ID, etc.",
    )
    year = df.NumberFilter(label="Year", help_text="Year of publication")
    journal = df.CharFilter(lookup_expr="icontains", label="Journal")
    title = df.CharFilter(lookup_expr="icontains", label="Title")
    authors = df.CharFilter(method="filter_authors", label="Authors")
    abstract = df.CharFilter(lookup_expr="icontains", label="Abstract")
    tags = df.ModelMultipleChoiceFilter(
        queryset=models.ReferenceFilterTag.objects.all(),
        method="filter_tags",
        conjoined=True,
        label="Tags",
        help_text="Select one or more tags. If a parent tag is selected, tag children are also considered a match. If multiple tags are selected, references must include all selected tags (or their children).",
    )
    order_by = df.OrderingFilter(
        fields=(
            ("authors", "authors"),
            ("year", "year"),
        ),
    )
    paginate_by = PaginationFilter()

    class Meta:
        model = models.Reference
        fields = [
            "id",
            "db_id",
            "year",
            "journal",
            "title",
            "authors",
            "abstract",
            "tags",
            "order_by",
            "paginate_by",
        ]
        grid_layout = {
            "rows": [
                {"columns": [{"width": 3}, {"width": 3}, {"width": 3}, {"width": 3}]},
                {
                    "columns": [
                        {
                            "width": 5,
                            "rows": [{"columns": [{"width": 12}, {"width": 12}, {"width": 12}]}],
                        },
                        {"width": 7},
                    ]
                },
                {"columns": [{"width": 3}, {"width": 3}]},
            ]
        }

    def filter_authors(self, queryset, name, value):
        query = Q(authors_short__unaccent__icontains=value) | Q(authors__unaccent__icontains=value)
        return queryset.filter(query)

    def filter_tags(self, queryset, name, value):
        for tag in value:
            tag_ids = list(tag.get_tree(parent=tag).values_list("id", flat=True))
            queryset = queryset.filter(tags__in=tag_ids)
        return queryset.distinct()

    def prefilter_queryset(self, queryset):
        return queryset.filter(assessment=self.assessment)

    def change_form(self, form):
        tags = models.ReferenceFilterTag.get_assessment_qs(self.assessment.id)
        form.fields["tags"].queryset = tags
        form.fields["tags"].label_from_instance = lambda tag: tag.get_nested_name()
        return form
