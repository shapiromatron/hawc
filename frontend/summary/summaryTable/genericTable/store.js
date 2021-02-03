import _ from "lodash";
import {action, autorun, computed, observable} from "mobx";

const createCell = function(row, column) {
    return {
        row,
        column,
        header: row === 0,
        col_span: 1,
        row_span: 1,
        quill_text: "<p>...</p>",
    };
};

class GenericTableStore {
    @observable editMode = false;
    @observable settings = null;
    @observable editingCellIndex = null;
    @observable showCellModal = false;

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

    @action.bound editSelectedCell(row, column) {
        this.editingCellIndex = _.findIndex(this.settings.cells, {row, column});
        this.showCellModal = true;
    }

    @action.bound hideCellModal() {
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

    @computed get editCell() {
        if (!_.isFinite(this.editingCellIndex)) {
            return null;
        }
        return this.settings.cells[this.editingCellIndex];
    }

    @computed get bodyRowIndexes() {
        return _.chain(this.settings.cells)
            .filter(d => d.header === false)
            .map(d => d.row)
            .uniq()
            .value();
    }

    @computed get headerRowIndexes() {
        // NOTE - rows may in both header and body if header is true AND false; make sure this is
        // updated for all cells in a row
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

    // these methods send/return data to and from the parent object
    @action.bound updateSettings(settings) {
        this.settings = settings;
    }
    @computed get getSettingsJson() {
        return JSON.stringify(this.settings);
    }
}

export default GenericTableStore;
