import {action, autorun, computed, observable} from "mobx";

const dataUrl = id => `/ani/api/assessment/${id}/endpoint-doses-heatmap/`;

class StudyOutcomeTableStore {
    @observable editMode = false;
    @observable settings = null;
    @observable isFetchingData = false;
    @observable dataset = null;

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
        return this.dataset !== null;
    }

    @action.bound fetchData() {
        if (this.isFetchingData === true) {
            return;
        }
        this.isFetchingData = true;
        const url = dataUrl(this.table.assessment);
        fetch(url)
            .then(d => d.json())
            .then(d => {
                this.dataset = d;
            });
    }
    @action.bound addRow() {
        console.log("addRow");
    }
    @action.bound moveRow(row, offset) {
        console.log("moveRow");
    }
    @action.bound moveColumn(column, offset) {
        console.log("moveColumn");
    }
    @action.bound addColumn() {
        console.log("addColumn");
    }
    @action.bound deleteRow(row) {
        console.log("deleteRow");
    }
    @action.bound deleteColumn(column) {
        console.log("deleteColumn");
    }

    // inject new settings from parent object
    @action.bound updateSettings(settings) {
        this.settings = settings;
    }
}

export default StudyOutcomeTableStore;
