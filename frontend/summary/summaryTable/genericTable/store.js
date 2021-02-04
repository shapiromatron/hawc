import _ from "lodash";
import {action, autorun, computed, observable, toJS} from "mobx";

import h from "shared/utils/helpers";

// TODO - add colwidths
// TODO - delete row
// TODO - delete column
// TODO - move row up/down
// TODO - move column left/right

const createCell = function(row, column) {
        return {
            row,
            column,
            header: row === 0,
            col_span: 1,
            row_span: 1,
            quill_text: "<p>...</p>",
        };
    },
    sortCells = function(cells) {
        return _.chain(cells)
            .sortBy(d => d.column)
            .sortBy(d => d.row)
            .value();
    },
    cellRangeSearch = function(cells, row, column) {
        return _.find(cells, cell => {
            return (
                row >= cell.row &&
                row < cell.row + cell.row_span &&
                column >= cell.column &&
                column < cell.column + cell.col_span
            );
        });
    },
    anyMergedCells = function(cellsToTest, matrix) {
        return _.chain(cellsToTest)
            .map(d => {
                let match = matrix[d.row][d.column];
                return match.row_span > 1 || match.col_span > 1;
            })
            .some()
            .value();
    };

class GenericTableStore {
    @observable editMode = false;
    @observable settings = null;
    @observable editingCellIndex = null;
    @observable showCellModal = false;
    @observable stagedCell = null;
    @observable quickEditCell = null;
    @observable editCellErrorText = "";

    constructor(editMode, settings, editRootStore) {
        this.editMode = editMode;
        this.settings = settings;
        this.editRootStore = editRootStore;
        if (editMode && editRootStore) {
            autorun(() => {
                this.editRootStore.updateTableContent(JSON.stringify(this.settings), false);
            });
        }
    }

    @action.bound selectCellEdit(cell, quick) {
        // just the text
        this.editingCellIndex = _.findIndex(this.settings.cells, {
            row: cell.row,
            column: cell.column,
        });
        this.stagedCell = _.cloneDeep(toJS(cell));
        if (quick) {
            this.showCellModal = false;
            this.quickEditCell = cell;
        } else {
            this.quickEditCell = null;
            this.showCellModal = true;
        }
    }

    @action.bound saveCellChanges() {
        // returns true if cell was changed, false if otherwise
        const oldCell = this.settings.cells[this.editingCellIndex],
            newCell = this.stagedCell;

        // book-keeping; if we've merged/unmerged cells, create/delete duplicates
        if (oldCell.row_span != newCell.row_span || oldCell.col_span != newCell.col_span) {
            const newCellRange = {},
                oldCellRange = {};

            let r,
                c,
                cells = _.cloneDeep(this.settings.cells);

            for (r = newCell.row; r < newCell.row + newCell.row_span; r++) {
                for (c = newCell.column; c < newCell.column + newCell.col_span; c++) {
                    newCellRange[`${r}-${c}`] = {row: r, column: c};
                }
            }

            for (r = newCell.row; r < newCell.row + oldCell.row_span; r++) {
                for (c = newCell.column; c < newCell.column + oldCell.col_span; c++) {
                    oldCellRange[`${r}-${c}`] = {row: r, column: c};
                }
            }

            const newCellKeys = new Set(_.keys(newCellRange)),
                oldCellKeys = new Set(_.keys(oldCellRange)),
                cellsToDelete = h.setDifference(newCellKeys, oldCellKeys).map(d => newCellRange[d]),
                cellsToAdd = h
                    .setDifference(oldCellKeys, newCellKeys)
                    .map(d => oldCellRange[d])
                    .map(d => createCell(d.row, d.column));

            if (anyMergedCells(cellsToDelete, this.cellMatrix)) {
                console.error("cannot merge cells; cells are merged");
                this.editCellErrorText = "Cannot merge cells; intersects with other merged cells.";
                return false;
            }

            if (cellsToDelete.length > 0) {
                cells = cells.filter(cell => {
                    return _.findIndex(cellsToDelete, {row: cell.row, column: cell.column}) == -1;
                });
            }
            cells.push(...cellsToAdd);
            this.settings.cells = sortCells(cells);
        }

        // update current cell; index may have changed so we fetch again
        const index = _.findIndex(this.settings.cells, {
            row: this.stagedCell.row,
            column: this.stagedCell.column,
        });
        this.settings.cells[index] = this.stagedCell;
        this.editCellErrorText = "";
        return true;
    }

    @action.bound closeEditModal(saveChanges) {
        if (saveChanges) {
            const success = this.saveCellChanges();
            if (!success) {
                return;
            }
        }
        this.editCellErrorText = "";
        this.stagedCell = null;
        this.quickEditCell = null;
        this.editingCellIndex = null;
        this.showCellModal = false;
    }

    @action.bound addRow() {
        const row = this.totalRows,
            cols = this.totalColumns,
            newCells = _.range(cols).map(column => createCell(row, column));
        this.settings.cells.push(...newCells);
    }

    @action.bound addColumn() {
        const rows = this.totalRows,
            col = this.totalColumns,
            newCells = _.range(rows).map(row => createCell(row, col));
        this.settings.cells.push(...newCells);
    }

    @action.bound updateStagedValue(name, value) {
        this.stagedCell[name] = value;
    }

    @computed get cellMatrix() {
        let r, c, row, matrix;
        matrix = [];
        for (r = 0; r < this.totalRows; r++) {
            row = [];
            for (c = 0; c < this.totalColumns; c++) {
                row.push(cellRangeSearch(this.settings.cells, r, c));
            }
            matrix.push(row);
        }
        return matrix;
    }

    @computed get editCell() {
        if (!_.isFinite(this.editingCellIndex)) {
            return null;
        }
        return this.settings.cells[this.editingCellIndex];
    }

    @computed get showHeaderInput() {
        // only first 2 rows can be headers
        return this.editCell.row < 2;
    }

    @computed get getMaxColSpanRange() {
        const cols = this.totalColumns,
            col = this.editCell.column,
            range = cols + 1 - col,
            maxRange = Math.max(0, range - 1);

        return maxRange;
    }

    @computed get getMaxRowSpanRange() {
        const rows = this.totalRows,
            row = this.editCell.row,
            range = rows + 1 - row,
            maxRange = Math.max(0, range - 1);

        return maxRange;
    }

    @computed get bodyRowIndexes() {
        const headers = new Set(this.headerRowIndexes);
        return _.chain(this.settings.cells)
            .filter(d => d.header === false && !headers.has(d.row))
            .map(d => d.row)
            .uniq()
            .value();
    }

    @computed get headerRowIndexes() {
        // if any cell is marked as a header, it's a header
        return _.chain(this.settings.cells)
            .filter(d => d.header === true)
            .map(d => d.row)
            .uniq()
            .value();
    }

    @computed get cellsByRow() {
        return _.chain(this.settings.cells)
            .groupBy("row")
            .value();
    }

    @computed get totalRows() {
        return _.chain(this.settings.cells)
            .map(d => d.row + d.row_span)
            .max()
            .value();
    }
    @computed get totalColumns() {
        return _.chain(this.settings.cells)
            .map(d => d.column + d.col_span)
            .max()
            .value();
    }

    @computed get colWidthStyle() {
        const percentage = Math.round(100 / this.totalColumns);
        return _.range(this.totalColumns).map(d => {
            return {width: `${percentage}%`};
        });
    }

    // these methods send/return data to and from the parent object
    @action.bound updateSettings(settings) {
        this.settings = settings;
    }
    @computed get getSettingsJson() {
        return JSON.stringify(this.settings);
    }
}

export default GenericTableStore;
