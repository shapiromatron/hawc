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
        method="filter_tags",
        conjoined=True,
        label="Tags",
        help_text="If multiple tags are selected, references must include all selected tags.",
    )
    tag_choice = df.ChoiceFilter(
        method=filter_noop,
        choices=TagChoices.choices,
        label="Tag choice",
    )
    include_descendants = df.BooleanFilter(
        method=filter_noop, widget=CheckboxInput(), label="Include tag descendants"
    )
    untagged = df.BooleanFilter(
        method="filter_untagged", widget=CheckboxInput(), label="Untagged only"
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
            "title_abstract",
            "authors",
            "search",
            "tags",
            "tag_choice",
            "include_descendants",
            "untagged",
            "order_by",
            "paginate_by",
        ]

    def get_tag_choice(self) -> TagChoices:
        # tag choices are only provided with conflict resolution enabled
        if not self.assessment.literature_settings.conflict_resolution:
            return TagChoices.RESOLVED
        try:
            return TagChoices(self.data.get("tag_choice"))
        except ValueError:
            # the default for conflict resolution is to use resolved and user tags
            return TagChoices.RESOLVED_AND_USER

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
        tag_choice = self.get_tag_choice()

        for tag in value:
            tag_ids = (
                list(tag.get_tree(parent=tag).values_list("id", flat=True))
                if include_descendants
                else [tag]
            )
            resolved_query = Q(tags__in=tag_ids)
            user_query = Q(user_tags__tags__in=tag_ids, user_tags__is_resolved=False)
            mine_query = Q(
                user_tags__tags__in=tag_ids,
                user_tags__is_resolved=False,
                user_tags__user=self.request.user,
            )
            if tag_choice == TagChoices.RESOLVED_AND_USER:
                query = resolved_query | user_query
            elif tag_choice == TagChoices.RESOLVED_AND_MINE:
                query = resolved_query | mine_query
            elif tag_choice == TagChoices.RESOLVED:
                query = resolved_query
            elif tag_choice == TagChoices.USER:
                query = user_query
            elif tag_choice == TagChoices.MINE:
                query = mine_query
            queryset = queryset.filter(query)
        return queryset.distinct()

    def filter_untagged(self, queryset, name, value):
        if not value:
            return queryset
        tag_choice = self.get_tag_choice()
        if tag_choice == TagChoices.RESOLVED_AND_USER:
            return queryset.annotate(
                resolved_tag_count=Count("tags"),
                user_tag_count=Count("user_tags", filter=Q(user_tags__is_resolved=False)),
            ).filter(resolved_tag_count=0, user_tag_count=0)
        elif tag_choice == TagChoices.RESOLVED_AND_MINE:
            return queryset.annotate(
                resolved_tag_count=Count("tags"),
                user_tag_count=Count(
                    "user_tags",
                    filter=Q(user_tags__is_resolved=False) & Q(user_tags__user=self.request.user),
                ),
            ).filter(resolved_tag_count=0, user_tag_count=0)
        elif tag_choice == TagChoices.RESOLVED:
            return queryset.annotate(resolved_tag_count=Count("tags")).filter(resolved_tag_count=0)
        elif tag_choice == TagChoices.USER:
            return queryset.annotate(
                user_tag_count=Count("user_tags", filter=Q(user_tags__is_resolved=False))
            ).filter(user_tag_count=0)
        elif tag_choice == TagChoices.MINE:
            return queryset.annotate(
                user_tag_count=Count(
                    "user_tags",
                    filter=Q(user_tags__is_resolved=False) & Q(user_tags__user=self.request.user),
                )
            ).filter(user_tag_count=0)

    def create_form(self):
        form = super().create_form()
        if "tags" in form.fields:
            tags = models.ReferenceFilterTag.get_assessment_qs(self.assessment.id)
            form.fields["tags"].queryset = tags
            form.fields["tags"].label_from_instance = lambda tag: tag.get_nested_name()
            form.fields["tags"].widget.attrs["size"] = 8
        if "search" in form.fields:
            form.fields["search"].queryset = models.Search.objects.filter(
                assessment=self.assessment
            )
        if "tag_choice" in form.fields:
            if not self.assessment.literature_settings.conflict_resolution:
                form.fields["tag_choice"].disabled = True
        return form
