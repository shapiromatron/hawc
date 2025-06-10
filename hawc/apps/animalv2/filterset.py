import django_filters as df

from ..common.filterset import ArrowOrderingFilter, BaseFilterSet, InlineFilterForm
from . import models


class ObservationOrderingFilter(ArrowOrderingFilter):
    def filter(self, qs, value):
        ordering = [self.get_ordering_value(param) for param in value]
        return qs.order_by(*ordering)


class ObservationFilterSet(BaseFilterSet):
    endpoint_target = df.CharFilter(
        lookup_expr="icontains",
        field_name="endpoint__name",
        label="Effect Subtype",
        help_text="Filter by effect subtype",
    )
    tested_status = df.ChoiceFilter(
        empty_label="- Tested Status -",
        choices=[(True, True), (False, False)],
    )
    reported_status = df.ChoiceFilter(
        empty_label="- Reported Status -",
        choices=[(True, True), (False, False)],
    )
    order_by = ObservationOrderingFilter(
        label="Ordering",
        fields=(
            ("endpoint__parent__parent__name", "system"),
            ("endpoint__parent__name", "effect"),
            ("endpoint__name", "effect subtype"),
        ),
        initial="system",
    )

    class Meta:
        model = models.Observation
        form = InlineFilterForm
        fields = ["endpoint_target", "tested_status", "reported_status", "order_by"]
        main_field = "endpoint_target"
        appended_fields = ["tested_status", "reported_status", "order_by"]

    def filter(self, items: list[models.Observation]) -> list[models.Observation]:
        # custom method that acts on a list, not a QuerySet; mirrors parent implementation
        if self.is_bound:
            self.errors  # noqa: B018 - this is not a noop; checks for validation errors
            items = self._filter(items)
        return items

    def _filter(self, items):
        # filter
        for name, value in self.form.cleaned_data.items():
            if not value:
                continue
            if name == "tested_status":
                status = False if value == "False" else True
                items = [item for item in items if item.tested_status == status]
            elif name == "reported_status":
                status = False if value == "False" else True
                items = [item for item in items if item.reported_status == status]
            elif name == "endpoint_target":
                items = [item for item in items if value in item.endpoint.name]

        # sort
        ordering = self.form.cleaned_data.get("order_by", ["system"])[0]
        descending = "-" in ordering
        sort_by = ordering.replace("-", "")
        sort_key_functions = {
            "effect subtype": lambda x: x.endpoint.name,
            "effect": lambda x: x.endpoint.parent.name,
            "system": lambda x: x.endpoint.parent.parent.name,
        }
        items = sorted(items, key=sort_key_functions[sort_by], reverse=descending)

        return items
