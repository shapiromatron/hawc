from selectable.base import ModelLookup


class DistinctStringLookup(ModelLookup):
    """
    Return distinct strings for a single CharField in a model
    """
    distinct_field = None

    def get_query(self, request, term):
        self.search_fields = (self.distinct_field + "__icontains", )
        return super(DistinctStringLookup, self)\
            .get_query(request, term)\
            .order_by(self.distinct_field)\
            .distinct(self.distinct_field)

    def get_item_value(self, item):
        return getattr(item, self.distinct_field)

    def get_item_label(self, item):
        return self.get_item_value(item)


class RelatedLookup(ModelLookup):
    related_filter = None  # filter-string

    def get_query(self, request, term):
        try:
            id_ = int(request.GET.get('related', -1))
        except ValueError:
            id_ = -1
        self.filters.update({self.related_filter: id_})
        return super(RelatedLookup, self).get_query(request, term)
