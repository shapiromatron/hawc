import django_filters as df
from django.db.models import Q

from ..common.filterset import (
    BaseFilterSet,
    FilterForm,
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
        help_text="Search by cause, effect, study, design, or result name",
    )
    order_by = df.OrderingFilter(
        fields=(
            ("design__study__short_citation", "study"),
            ("name", "result name"),
        ),
        choices=(
            ("study", "study"),
            ("result name", "name"),
        ),
        empty_label=("Default Order"),
    )
    paginate_by = PaginationFilter(empty_label="Default Pagination")

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
