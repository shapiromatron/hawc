import django_filters as df
from django.db.models import Count, Q
from django.forms.widgets import CheckboxInput
from django_filters import FilterSet

from ..common.filterset import (
    ArrowOrderingFilter,
    BaseFilterSet,
    ExpandableFilterForm,
    PaginationFilter,
    filter_noop,
)
from . import models


class ReferenceFilterSet(BaseFilterSet):
    id = df.NumberFilter(label="HAWC ID", help_text="HAWC reference ID.")
    db_id = df.CharFilter(
        field_name="identifiers__unique_id",
        lookup_expr="icontains",
        label="External identifier",
        help_text="Pubmed ID, DOI, HERO ID",
    )
    journal = df.CharFilter(lookup_expr="icontains", label="Journal")
    ref_search = df.CharFilter(
        method="filter_search",
        label="Title/Author/Year",
        help_text="Filter citations (authors, year, title)",
    )
    search = df.ModelChoiceFilter(
        field_name="searches", queryset=models.Search.objects.all(), label="Search/Import"
    )
    authors = df.CharFilter(method="filter_authors", label="Authors")
    year = df.NumberFilter(label="Year")
    tags = df.ModelMultipleChoiceFilter(
        queryset=models.ReferenceFilterTag.objects.all(),
        null_value="untagged",
        null_label="[Untagged]",
        method="filter_tags",
        conjoined=True,
        label="Tags",
        help_text="Select a tag to view references with that specific tag. Choose [Untagged] to view references without any tags. If multiple tags are selected, references must include all selected tags.",
    )
    include_descendants = df.BooleanFilter(
        method=filter_noop,
        widget=CheckboxInput(),
        label="Include tag descendants",
        help_text="Applies to tags selected above. By default, only references with the specific selected tag(s) are shown; checking this box includes references that are tagged with any descendant of the selected tag",
    )
    anything_tagged = df.BooleanFilter(
        method="filter_anything_tagged",
        widget=CheckboxInput(),
        label="Anything tagged",
        help_text="Check box to view references with at least one tag applied",
    )
    my_tags = df.ModelMultipleChoiceFilter(
        queryset=models.ReferenceFilterTag.objects.all(),
        null_value="untagged",
        null_label="[Untagged]",
        method="filter_my_tags",
        conjoined=True,
        label="My Tags",
        help_text="Select a tag to view references you have applied that specific tag to. Choose [Untagged] to view references that you have not tagged. If multiple tags are selected, references must include all selected tags.",
    )
    include_mytag_descendants = df.BooleanFilter(
        method=filter_noop,
        widget=CheckboxInput(),
        label="Include tag descendants",
        help_text="Applies to tags selected above. By default, only references with the specific selected tag(s) are shown; checking this box includes references that are tagged with any descendant of the selected tag",
    )
    anything_tagged_me = df.BooleanFilter(
        method="filter_anything_tagged_me",
        widget=CheckboxInput(),
        label="Tagged by me",
        help_text="All references that you have tagged",
    )
    order_by = ArrowOrderingFilter(
        initial="-year",
        fields=(
            ("authors_short", "authors"),
            ("year", "year"),
        ),
    )
    needs_tagging = df.BooleanFilter(
        method="filter_needs_tagging",
        widget=CheckboxInput(),
        label="Needs Tagging",
        help_text="References tagged by less than two people",
    )
    partially_tagged = df.BooleanFilter(
        method="filter_partially_tagged",
        widget=CheckboxInput(),
        label="Partially Tagged",
        help_text="References with one unresolved user tag",
    )
    workflow = df.ModelChoiceFilter(
        method="filter_workflow",
        queryset=models.Workflow.objects.all(),
        label="Workflow",
        empty_label="[No Workflow]",
    )
    paginate_by = PaginationFilter()

    class Meta:
        model = models.Reference
        form = ExpandableFilterForm
        fields = [
            "id",
            "db_id",
            "journal",
            "ref_search",
            "authors",
            "year",
            "search",
            "tags",
            "include_descendants",
            "anything_tagged",
            "my_tags",
            "include_mytag_descendants",
            "anything_tagged_me",
            "order_by",
            "paginate_by",
            "partially_tagged",
            "needs_tagging",
            "workflow",
        ]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.filter(assessment=self.assessment)

    def filter_authors(self, queryset, name, value):
        query = Q(authors_short__unaccent__icontains=value) | Q(authors__unaccent__icontains=value)
        return queryset.filter(query)

    def filter_search(self, queryset, name, value):
        return queryset.full_text_search(value)

    def filter_tags(self, queryset, name, value):
        include_descendants = self.data.get("include_descendants", False)

        for tag in value:
            if tag == "untagged":
                queryset = queryset.filter(tags__isnull=True)
            else:
                tag_ids = (
                    list(tag.get_tree(parent=tag).values_list("id", flat=True))
                    if include_descendants
                    else [tag.id]
                )
                queryset = queryset.filter(tags__in=tag_ids)
        return queryset.distinct()

    def filter_anything_tagged(self, queryset, name, value):
        if not value:
            return queryset
        queryset = queryset.filter(tags__isnull=False)
        return queryset.distinct()

    def filter_my_tags(self, queryset, name, value):
        include_descendants = self.data.get("include_mytag_descendants", False)
        for tag in value:
            if tag == "untagged":
                queryset = queryset.annotate(
                    user_tag_count=Count(
                        "user_tags",
                        filter=Q(user_tags__is_resolved=False)
                        & Q(user_tags__user=self.request.user),
                    )
                ).filter(user_tag_count=0)
            else:
                tag_ids = (
                    list(tag.get_tree(parent=tag).values_list("id", flat=True))
                    if include_descendants
                    else [tag.id]
                )
                queryset = queryset.annotate(
                    mytag_count=Count(
                        "user_tags",
                        filter=Q(user_tags__tags__in=tag_ids)
                        & Q(user_tags__is_resolved=False)
                        & Q(user_tags__user=self.request.user),
                    )
                ).filter(mytag_count__gt=0)
        return queryset.distinct()

    def filter_anything_tagged_me(self, queryset, name, value):
        if not value:
            return queryset
        queryset = queryset.annotate(
            my_tag_count=Count(
                "user_tags",
                filter=Q(user_tags__is_resolved=False) & Q(user_tags__user=self.request.user),
            )
        ).filter(my_tag_count__gt=0)
        return queryset.distinct()

    def filter_partially_tagged(self, queryset, name, value):
        if not value:
            return queryset
        queryset = queryset.annotate(
            user_tag_count=Count("user_tags", filter=Q(user_tags__is_resolved=False))
        ).filter(user_tag_count=1)
        return queryset.distinct()

    def filter_needs_tagging(self, queryset, name, value):
        if not value:
            return queryset
        queryset = queryset.annotate(
            user_tag_count=Count("user_tags", filter=Q(user_tags__is_resolved=False))
        )
        queryset = queryset.filter(user_tag_count__lt=2)
        return queryset.distinct()

    def filter_workflow(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(value.get_filters()).distinct()

    def create_form(self):
        form = super().create_form()
        for field in [
            "partially_tagged",
            "tags",
            "my_tags",
            "anything_tagged",
            "anything_tagged_me",
            "include_mytag_descendants",
            "include_descendants",
            "needs_tagging",
        ]:
            if field in form.fields:
                form.fields[field].hover_help = True
        if "tags" in form.fields:
            tags = models.ReferenceFilterTag.get_assessment_qs(self.assessment.id)
            form.fields["tags"].queryset = tags
            form.fields["tags"].label_from_instance = lambda tag: tag.get_nested_name()
            form.fields["tags"].widget.attrs["size"] = 8
        if "my_tags" in form.fields:
            tags = models.ReferenceFilterTag.get_assessment_qs(self.assessment.id)
            form.fields["my_tags"].queryset = tags
            form.fields["my_tags"].label_from_instance = lambda tag: tag.get_nested_name()
            form.fields["my_tags"].widget.attrs["size"] = 8
            form.fields["tags"].label = "Consensus Tags"
        if "search" in form.fields:
            form.fields["search"].queryset = models.Search.objects.filter(
                assessment=self.assessment
            )
        if "workflow" in form.fields:
            form.fields["workflow"].queryset = models.Workflow.objects.filter(
                assessment=self.assessment
            )
        return form


class ReferenceExportFilterSet(FilterSet):
    searches = df.ModelChoiceFilter(queryset=models.Search.objects.all())
    tag = df.ModelChoiceFilter(
        queryset=models.ReferenceFilterTag.objects.all(), method="filter_tag"
    )
    include_descendants = df.BooleanFilter(method=filter_noop)
    table_builder = df.BooleanFilter(method=filter_noop)

    class Meta:
        model = models.Reference
        fields = [
            "searches",
            "tag",
            "include_descendants",
        ]

    def filter_tag(self, queryset, name, value):
        include_descendants = self.data.get("include_descendants", False)
        return queryset.with_tag(tag=value, descendants=include_descendants)
