from selectable.base import ModelLookup
from selectable.registry import registry

from . import models


class DataPivotLookup(ModelLookup):
    model = models.DataPivot
    search_fields = ('title__icontains', )

    def get_query(self, request, term):
        try:
            pk = int(request.GET.get('assessment_id'))
            self.filters = {'assessment_id': pk}
        except Exception:
            return self.model.objects.none()
        return super(DataPivotLookup, self).get_query(request, term)


class VisualLookup(ModelLookup):
    model = models.Visual
    search_fields = ('title__icontains', )

    def get_query(self, request, term):
        try:
            pk = int(request.GET.get('assessment_id'))
            self.filters = {'assessment_id': pk}
        except Exception:
            return self.model.objects.none()
        return super(VisualLookup, self).get_query(request, term)


registry.register(DataPivotLookup)
registry.register(VisualLookup)
