import _ from "lodash";
import {action, computed, observable} from "mobx";

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

    constructor(editMode, settings, editRootStore) {
        this.editMode = editMode;
        this.settings = settings;
        this.editRootStore = editRootStore;
    }

    @action.bound editCell(row, col) {
        console.log("editing cell", row, col);
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
