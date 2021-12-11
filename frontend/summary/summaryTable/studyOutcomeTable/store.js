import _ from "lodash";
import {action, autorun, computed, observable} from "mobx";

import * as constants from "./constants";

class StudyOutcomeTableStore {
    @observable editMode = false;
    @observable settings = null;
    @observable isFetchingData = false;
    @observable dataset = null;
    @observable showRowCreateForm = false;
    @observable showColumnCreateForm = false;
    @observable editColumnIndex = null;
    @observable editRowIndex = null;

    constructor(editMode, table, editRootStore) {
        this.editMode = editMode;
        this.table = table;
        this.settings = table.content;
        this.editRootStore = editRootStore;
        if (editMode && editRootStore) {
            autorun(() => {
                this.editRootStore.updateTableContent(JSON.stringify(this.settings), false);
            });
        }
    }

    @computed get numRows() {
        return this.settings.rows.length;
    }
    @computed get numColumns() {
        return this.settings.columns.length;
    }
    @computed get hasData() {
        return this.dataset !== null && this.dataset.length > 0;
    }

    // row attributes
    @computed get rowTypeChoices() {
        return constants.rowTypeChoices;
    }
    @computed get rowIdChoices() {
        return _.chain(this.dataset)
            .uniqBy("study id")
            .map(d => {
                return {id: d["study id"], label: d["study citation"]};
            })
            .value();
    }

    @action.bound setEditColumnIndex(idx) {
        this.editColumnIndex = idx;
    }
    @action.bound setEditRowIndex(idx) {
        this.editRowIndex = idx;
    }

    @action.bound fetchData() {
        if (this.hasData || this.isFetchingData) {
            return;
        }
        const url = constants.dataUrl(this.table.assessment);
        this.isFetchingData = true;
        fetch(url)
            .then(d => d.json())
            .then(d => {
                this.dataset = d;
                this.isFetchingData = false;
            });
    }
    @action.bound toggleShowCreateRowForm() {
        this.showRowCreateForm = !this.showRowCreateForm;
    }
    @action.bound toggleColumnCreateRowForm() {
        this.showColumnCreateForm = !this.showColumnCreateForm;
    }
    @action.bound createRow() {
        const rows = this.rowIdChoices;
        if (rows.length > 0) {
            const item = constants.createNewRow(rows[0].id);
            this.settings.rows.push(item);
        }
    }
    @action.bound createColumn() {
        this.settings.columns.push(constants.createNewColumn());
    }
    @action.bound moveRow(rowIdx, offset) {
        if (rowIdx + offset >= 0 && rowIdx + offset < this.numRows) {
            const r1 = this.settings.rows[rowIdx],
                r2 = this.settings.rows[rowIdx + offset];
            this.settings.rows[rowIdx] = r2;
            this.settings.rows[rowIdx + offset] = r1;
            this.setEditRowIndex(rowIdx + offset);
        }
    }
    @action.bound moveColumn(colIdx, offset) {
        if (colIdx + offset >= 0 && colIdx + offset < this.numColumns) {
            const c1 = this.settings.columns[colIdx],
                c2 = this.settings.columns[colIdx + offset];
            this.settings.columns[colIdx] = c2;
            this.settings.columns[colIdx + offset] = c1;
            this.setEditColumnIndex(colIdx + offset);
        }
    }
    @action.bound deleteRow(rowIdx) {
        this.settings.rows.splice(rowIdx, 1);
        this.setEditRowIndex(null);
    }
    @action.bound deleteColumn(columnIdx) {
        this.settings.columns.splice(columnIdx, 1);
        this.setEditColumnIndex(null);
    }

    // inject new settings from parent object
    @action.bound updateSettings(settings) {
        this.settings = settings;
    }
}

export default StudyOutcomeTableStore;
