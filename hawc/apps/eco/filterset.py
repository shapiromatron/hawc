import django_filters as df
from django.db.models import Q

from ..common.filterset import (
    ArrowOrderingFilter,
    BaseFilterSet,
    InlineFilterForm,
    PaginationFilter,
)
from . import models


class NestedTermFilterSet(BaseFilterSet):
    class Meta:
        model = models.NestedTerm
        form = InlineFilterForm
        fields = {
            "name": ["contains"],
        }
        main_field = "name__contains"

    @property
    def has_query(self) -> bool:
        return self.data.get("name__contains", "") != ""


class ResultFilterSet(BaseFilterSet):
    search = df.CharFilter(
        method="filter_search",
        label="Search",
        help_text="Search by study, design, cause, effect, or result",
    )
    order_by = ArrowOrderingFilter(
        fields=(
            ("design__study__short_citation", "study"),
            ("name", "result"),
        ),
        initial="study",
    )
    paginate_by = PaginationFilter()

    class Meta:
        model = models.Result
        form = InlineFilterForm
        fields = ["search", "order_by", "paginate_by"]
        grid_layout = {
            "rows": [
                {"columns": [{"width": 12}]},
            ]
        }

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        queryset = queryset.filter(design__study__assessment=self.assessment)
        if not self.perms["edit"]:
            queryset = queryset.filter(design__study__published=True)
        return queryset

    def filter_search(self, queryset, name, value):
        query = (
            Q(name__icontains=value)
            | Q(cause__name__icontains=value)
            | Q(cause__term__name__icontains=value)
            | Q(effect__name__icontains=value)
            | Q(effect__term__name__icontains=value)
            | Q(design__study__short_citation__icontains=value)
            | Q(design__name__icontains=value)
        )
        return queryset.filter(query)
