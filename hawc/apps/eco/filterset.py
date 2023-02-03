import django_filters as df

from ..common.filterset import BaseFilterSet


class NestedTermFilterset(BaseFilterSet):
    name = df.CharFilter(method="filter_name", label="Name")

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset)

    def filter_name(self, queryset, name, value):
        qs = queryset.filter(name__icontains=value)
        return qs
