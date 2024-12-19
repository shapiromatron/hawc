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
        choices=[
            (True, True),
            (False, False),
        ],
    )
    reported_status = df.ChoiceFilter(
        empty_label="- Reported Status -",
        choices=[
            (True, True),
            (False, False),
        ],
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def filter(self, observations):
        tested_status = self.request.GET.get("tested_status")
        reported_status = self.request.GET.get("reported_status")
        endpoint_target = self.request.GET.get("endpoint_target")
        order_by = self.request.GET.get("order_by", "-system")
        descending = order_by.startswith("-")

        if tested_status:
            status = False if tested_status == "False" else True
            observations = [item for item in observations if item.tested_status == status]
        if reported_status:
            status = False if reported_status == "False" else True
            observations = [item for item in observations if item.reported_status == status]
        if endpoint_target:
            observations = [item for item in observations if item.endpoint.name == endpoint_target]

        key_functions = {
            "effect subtype": lambda x: x.endpoint.name,
            "effect": lambda x: x.endpoint.parent.name,
            "system": lambda x: x.endpoint.parent.parent.name,
        }

        # set a default order
        if order_by not in key_functions.keys():
            order_by = "system"
            order_by = order_by.replace("-", "")

        observations = sorted(observations, key=key_functions[order_by], reverse=descending)
        return observations
