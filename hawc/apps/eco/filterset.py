
from ..common.filterset import BaseFilterSet, InlineFilterForm
from . import models


class NestedTermFilterSet(BaseFilterSet):

    class Meta:
        model = models.NestedTerm
        form = InlineFilterForm
        fields = {
            "name": ["contains"],
        }

    @property
    def has_query(self) -> bool:
        return self.data.get("name__contains", "") != ""
