from ..common.filterset import BaseFilterSet, InlineFilterForm
from . import models


class NestedTermFilterSet(BaseFilterSet):
    class Meta:
        model = models.NestedTerm
        form = InlineFilterForm
        fields = {
            "name": ["contains"],
        }
        main_field = "name__contains"
        grid_layout = {
            "rows": [{"columns": [{"width": 12}]}],
        }

    @property
    def has_query(self) -> bool:
        return self.data.get("name__contains", "") != ""
