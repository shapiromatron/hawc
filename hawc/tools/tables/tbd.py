from typing import List

from .base import BaseTable
from .generic import GenericCell
from .parser import tag_wrapper

## Table


class Table(BaseTable):
    # Add some object id validation? everything from same assessment at least
    data_columns: List
    data_ids: List
    judgment_columns: List
    judgments: List

    @property
    def column_headers(self):
        cells = []
        col = 0
        for column in self.data_columns:
            cell = GenericCell.parse_args(
                True, 0, col, 1, 1, tag_wrapper(column["label"], "p", "strong")
            )
            cells.append(cell)
            col += 1
        return cells

    @property
    def max_depth(self):
        # the deepest we go, ie study level, endpoint level, etc
        return max([column["depth"] for column in self.data_columns])

    def _get_data_ids(self, depth):
        # get all ids at given depth, used to query database
        if depth == 0:
            return self.data_ids[depth]
        return [id for id_list in self.data_ids[depth].values() for id in id_list]

    def _get_data(self):
        # TODO
        # Study.objects.filter(pk__in=self._get_data_ids(0)).in_bulk() # get a mapping at each depth, ie study at depth 0, endpoint at max depth
        # Remove keys from data_ids as we work our way down, ie id keys that don't map to objects ?
        depth_0 = {1: {"foo": "foo one"}, 2: {"foo": "foo two"}, 3: {"foo": "foo three"}}
        depth_1 = {
            1: {"bar": "bar one"},
            2: {"bar": "bar two"},
            3: {"bar": "bar three"},
            4: {"bar": "bar four"},
            5: {"bar": "bar five"},
            6: {"bar": "bar six"},
        }
        return [depth_0, depth_1]

    def _get_rowspan(self, depth, id):
        # rowspan at given depth and id, ie # of descendants
        if depth >= self.max_depth:
            return 1
        rows = 0
        for _id in self.data_ids[depth + 1][id]:
            rows += self._get_rowspan(depth + 1, _id)
        return rows

    def _get_ordered_ids(self, depth):
        # get ordered ids at given depth, used for constructing cells in correct order
        ids = self.data_ids[0]
        for d in range(1, depth + 1):
            ids = [next_id for old_id in ids for next_id in self.data_ids[d][old_id]]
        return ids

    def _set_cells(self):
        cells = []
        cells.extend(self.column_headers)
        data = self._get_data()
        row = 1
        col = 0
        # make this a cell group?
        for column in self.data_columns:
            row = 1
            depth = column["depth"]
            for id in self._get_ordered_ids(depth):
                text = tag_wrapper(data[depth][id][column["field"]], "p")
                rowspan = self._get_rowspan(depth, id)
                cell = GenericCell.parse_args(False, row, col, rowspan, 1, text)
                cells.append(cell)
                row += rowspan
            col += 1

        self.cells = cells

    @classmethod
    def get_default_props(cls):
        return {
            "data_columns": [
                {"label": "Foo", "field": "foo", "depth": 0},
                {"label": "Bar", "field": "bar", "depth": 1},
            ],
            "data_ids": [[1, 2, 3], {1: [1, 2, 3], 2: [4, 5], 3: [6]}],
            "judgment_columns": ["Judgment 1", "Judgment 2"],
            "judgments": [{"label": "L"}, {"label": "H"}],
        }
