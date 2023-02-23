from ..common.filterset import BaseFilterSet
from . import models


class NestedTermFilterSet(BaseFilterSet):
    class Meta:
        model = models.NestedTerm
        fields = {
            "name": ["contains"],
        }

    @property
    def has_query(self) -> bool:
        return self.data["name__contains"] != ""
