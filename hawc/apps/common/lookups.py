import operator
from functools import reduce
from typing import Any, Set

from django.db.models import Q
from django.forms import ValidationError
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

    def get_search_filter(self, request, term):
        return [Q(**{field: term}) for field in self.search_fields]

    def get_query(self, request, term):
        id_ = tryParseInt(request.GET.get("related"), -1)
        qs = self.get_queryset()
        search_fields = self.get_search_filter(request, term)
        return qs.filter(Q(**{self.related_filter: id_}) & reduce(operator.or_, search_fields))


class RelatedDistinctStringLookup(DistinctStringLookup):
    related_filter = None

    def get_query(self, request, term):
        qs = super().get_query(request, term)
        id_ = tryParseInt(request.GET.get("related"), -1)

        return qs.filter(Q(**{self.related_filter: id_}))


class UserSpecifiedRelatedLookup(RelatedLookup):
    # Return names of endpoints available for a particular study
    search_fields = None  # user choices below instead
    search_fields_choices: Set = set()
    order_by_choices: Set = set()

    def get_search_filter(self, request, term):
        """Return a valid search filter, from the available choices"""
        search_fields = request.GET.get("search_fields", "").split(",")
        if any(field not in self.search_fields_choices for field in search_fields):
            raise ValidationError("Invalid search fields specified")
        if not search_fields:
            raise ValidationError("At least one search field is required")

        request._search_fields = search_fields
        self._current_request = request
        fields = [f"{field}__icontains" for field in search_fields]
        return [Q(**{field: term}) for field in fields]

    def get_order_by(self, request):
        """Return a valid ordering column, from available choices"""
        order_by = request.GET.get("order_by", "id")
        if order_by not in self.order_by_choices:
            raise ValidationError(f"Invalid order_by: {order_by}")
        return order_by

    def get_query(self, request, term):
        order_by = self.get_order_by(request)
        return super().get_query(request, term).distinct().order_by(order_by)

    def get_item_label(self, obj):
        return " | ".join(
            [self._get_field_label(obj, field) for field in self._current_request._search_fields]
        )

    def get_item_value(self, obj):
        return self.get_item_label(obj)

    def _get_field_label(self, obj: Any, path: str) -> str:
        """Return label for a string-based  django ORM attribute path.

        For example, `related_item__some_field__foo` will return a str based representation
        of `obj.related_item.some_field.foo`.
        """
        item = obj
        for attribute in path.split("__"):
            item = getattr(item, attribute)
        return str(item)
