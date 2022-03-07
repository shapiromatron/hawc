import operator
from functools import reduce
from typing import Any

from django.db.models import Q
from selectable.base import ModelLookup

from .helper import tryParseInt


class DistinctStringLookup(ModelLookup):
    """
    Return distinct strings for a single CharField in a model
    """

    distinct_field = None

    def get_query(self, request, term):
        return (
            self.get_queryset()
            .filter(**{self.distinct_field + "__icontains": term})
            .order_by(self.distinct_field)
            .distinct(self.distinct_field)
        )

    def get_item_value(self, item):
        return getattr(item, self.distinct_field)

    def get_item_label(self, item):
        return self.get_item_value(item)


class RelatedLookup(ModelLookup):
    """
    Perform a search where related_filter is required, and search fields are
    ORd together. Ex:

        WHERE (self.related_filter = related_id) AND
              ( ... OR ... OR ...) for search fields
    """

    related_filter = None  # filter-string

    def get_query(self, request, term):
        id_ = tryParseInt(request.GET.get("related"), -1)

        qs = self.get_queryset()
        search_fields = [Q(**{field: term}) for field in self.search_fields]
        return qs.filter(Q(**{self.related_filter: id_}) & reduce(operator.or_, search_fields))

    def get_underscore_field_val(self, obj: Any, underscore_path: str) -> Any:
        """
        Recursively select attributes from objects, given a django queryset underscore path.
        For example, `related_item__some_field__foo` will return `obj.related_item.some_field.foo`

        Args:
            obj (Any): An object
            underscore_path (str): the path to retrieve

        Returns:
            Any: the desired attribute of the object or child object.
        """

        attr_whitelist = [
            "endpoint",
            "animal_group",
            "experiment",
            "name",
            "created",
            "last_updated",
            "data_type",
            "response_units",
            "observation_time",
            "system",
        ]
        obj_ = obj
        try:
            for attr in underscore_path.split("__"):
                if attr not in attr_whitelist:
                    raise AttributeError(f"Access to {obj_} attribute is not allowed.")
                obj_ = getattr(obj_, attr)
        except AttributeError:
            raise AttributeError(f"Element {underscore_path} not found in {obj}")

        return obj_


class RelatedDistinctStringLookup(DistinctStringLookup):
    related_filter = None

    def get_query(self, request, term):
        qs = super().get_query(request, term)
        id_ = tryParseInt(request.GET.get("related"), -1)

        return qs.filter(Q(**{self.related_filter: id_}))
