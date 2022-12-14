import django_filters as df
from django.db.models import Count, Q, TextChoices
from django.forms.widgets import CheckboxInput

from ..common.filterset import BaseFilterSet, PaginationFilter, filter_noop
from . import models


class TagChoices(TextChoices):
    RESOLVED_AND_USER = "resolved_and_user", "Resolved and user tags"
    RESOLVED_AND_MINE = "resolved_and_mine", "Resolved and my tags"
    RESOLVED = "resolved", "Only resolved tags"
    USER = "user", "Only user tags"
    MINE = "mine", "Only my tags"
    ZERO_USER = "zero_user", "Tagged by zero users"
    ONE_USER = "one_user", "Tagged by one user"
    TWO_PLUS_USERS = "two_plus_users", "Tagged by two or more users"


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
    title_abstract = df.CharFilter(method="filter_title_abstract", label="Title/Abstract")
    authors = df.CharFilter(method="filter_authors", label="Authors")
    search = df.ModelChoiceFilter(
        field_name="searches", queryset=models.Search.objects.all(), label="Search/Import"
    )
    tags = df.ModelMultipleChoiceFilter(
        queryset=models.ReferenceFilterTag.objects.all(),
        null_value="untagged",
        null_label="[Untagged]",
        method="filter_tags",
        conjoined=True,
        label="Tags",
        help_text="If multiple tags are selected, references must include all selected tags.",
    )
    include_descendants = df.BooleanFilter(
        method=filter_noop, widget=CheckboxInput(), label="Include tag descendants (resolved tags)"
    )
    anything_tagged = df.BooleanFilter(
        method="filter_anything_tagged", widget=CheckboxInput(), label="Show anything tagged"
    )
    my_tags = df.ModelMultipleChoiceFilter(
        queryset=models.ReferenceFilterTag.objects.all(),
        null_value="untagged",
        null_label="[Untagged]",
        method="filter_my_tags",
        conjoined=True,
        label="My Tags",
        help_text="If multiple tags are selected, references must include all selected tags.",
    )
    include_mytag_descendants = df.BooleanFilter(
        method=filter_noop, widget=CheckboxInput(), label="Include tag descendants (my tags)"
    )
    anything_tagged_me = df.BooleanFilter(
        method="filter_anything_tagged_me",
        widget=CheckboxInput(),
        label="Show anything tagged by me",
    )
    order_by = df.OrderingFilter(
        fields=(
            ("authors", "authors"),
            ("year", "year"),
        ),
        help_text="How results will be ordered",
    )
    needs_tagging = df.BooleanFilter(
        method="filter_needs_tagging",
        widget=CheckboxInput(),
        label="Needs Tagging",
    )
    paginate_by = PaginationFilter()

    class Meta:
        model = models.Reference
        fields = [
            "id",
            "db_id",
            "year",
            "journal",
            "title_abstract",
            "authors",
            "search",
            "tags",
            "include_descendants",
            "anything_tagged",
            "my_tags",
            "include_mytag_descendants",
            "anything_tagged_me",
            "order_by",
            "paginate_by",
            "needs_tagging",
        ]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.filter(assessment=self.assessment)

    def filter_authors(self, queryset, name, value):
        query = Q(authors_short__unaccent__icontains=value) | Q(authors__unaccent__icontains=value)
        return queryset.filter(query)

    def filter_title_abstract(self, queryset, name, value):
        query = Q(title__icontains=value) | Q(abstract__icontains=value)
        return queryset.filter(query)

    def filter_tags(self, queryset, name, value):
        include_descendants = self.data.get("include_descendants", False)

        for tag in value:
            if tag == "untagged":
                queryset = queryset.filter(tags__isnull=True)
            else:
                tag_ids = (
                    list(tag.get_tree(parent=tag).values_list("id", flat=True))
                    if include_descendants
                    else [tag]
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
                    else [tag]
                )
                queryset = queryset.filter(
                    user_tags__tags__in=tag_ids,
                    user_tags__is_resolved=False,
                    user_tags__user=self.request.user,
                )
        return queryset.distinct()

    def filter_anything_tagged_me(self, queryset, name, value):
        if not value:
            return queryset
        queryset = queryset.filter(user_tags__is_resolved=False, user_tags__user=self.request.user)
        return queryset.distinct()

    def filter_needs_tagging(self, queryset, name, value):
        if not value:
            return queryset
        queryset = queryset.annotate(
            user_tag_count=Count("user_tags", filter=Q(user_tags__is_resolved=False))
        )
        queryset = queryset.filter(user_tag_count__lt=2, tags__isnull=True)
        return queryset.distinct()

    def create_form(self):
        form = super().create_form()
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
        if "search" in form.fields:
            form.fields["search"].queryset = models.Search.objects.filter(
                assessment=self.assessment
            )
        return form
