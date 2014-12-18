from selectable.base import ModelLookup


class DistinctStringLookup(ModelLookup):
    """
    Return distinct strings for a single CharField in a model
    """
    distinct_field = None

    def get_query(self, request, term):
        any_case = self.distinct_field + "__icontains"
        filters = {any_case: term}
        return self.model.objects\
                   .filter(**filters)\
                   .distinct(self.distinct_field)

    def get_item_value(self, item):
        return getattr(item, self.distinct_field)

    def get_item_label(self, item):
        return getattr(item, self.distinct_field)

