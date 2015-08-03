import operator

from django.db.models import Q

from selectable.base import ModelLookup


class DistinctStringLookup(ModelLookup):
    """
    Return distinct strings for a single CharField in a model
    """
    distinct_field = None

    def get_query(self, request, term):
        return self.model.objects\
            .filter(**{self.distinct_field + "__icontains": term})\
            .order_by(self.distinct_field)\
            .distinct(self.distinct_field)

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
        try:
            id_ = int(request.GET.get('related', -1))
        except ValueError:
            id_ = -1
        search_fields = [
            Q(**{field: term})
            for field in self.search_fields
        ]
        return self.model.objects.filter(
            Q(**{self.related_filter: id_}) &
            reduce(operator.or_, search_fields)
        )
