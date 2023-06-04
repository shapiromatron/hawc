from ..common.filterset import BaseFilterSet, FilterForm
from . import models


class NestedTermFilterSet(BaseFilterSet):
    class Meta:
        model = models.NestedTerm
        form = FilterForm
        fields = {
            "name": ["contains"],
        }

    @property
    def has_query(self) -> bool:
        return self.data.get("name__contains", "") != ""
