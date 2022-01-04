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

    @observable stagedEdits = null;

    @action.bound updateStagedCell(rowIdx, colKey, value) {
        let row = this.stagedEdits.rows[rowIdx];
        row.customized = _.filter(row.customized, d => d.key != colKey);
        if (value != null) {
            row.customized.push(value);
        }
    }

    @action.bound updateStagedRow(rowIdx, value) {
        let row = this.stagedEdits.rows[rowIdx];
        if (
            ("type" in value && row.type !== value.type) ||
            ("id" in value && row.id !== value.id)
        ) {
            row.customized = [];
        }
        _.assign(row, value);
    }

    @action.bound updateStagedColumn(colIdx, value) {
        let col = this.stagedEdits.columns[colIdx];
        if ("attribute" in value && col.attribute !== value.attribute) {
            if (col.attribute == "rob_score") {
                delete col.metric_id;
            } else if (value.attribute == "rob_score") {
                let metric = this.metricIdChoices[0];
                col.metric_id = metric == null ? undefined : metric["id"];
            }
            this.stagedEdits.rows.forEach(row => {
                row.customized = _.filter(row.customized, d => d.key != col.key);
            });
        } else if ("metric_id" in value && col.metric_id !== value.metric_id) {
            this.stagedEdits.rows.forEach(row => {
                row.customized = _.filter(row.customized, d => d.key != col.key);
            });
        }
        _.assign(col, value);
    }

    @action.bound commitStagedEdits() {
        this.settings = this.stagedEdits;
        this.resetStagedEdits();
    }

    @action.bound resetStagedEdits() {
        this.editRowIndex = null;
        this.editColumnIndex = null;
        this.stagedEdits = null;
    }

    @action.bound setStagedEdits() {
        this.stagedEdits = _.cloneDeep(this.settings);
    }

    @computed get workingSettings() {
        return this.stagedEdits == null ? this.settings : this.stagedEdits;
    }

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
        return this.dataset !== null && this.dataset.data.length > 0;
    }

    // row attributes
    @computed get rowTypeChoices() {
        return constants.rowTypeChoices;
    }
    @computed get rowIdChoices() {
        return _.chain(this.dataset.data)
            .uniqBy("study id")
            .map(d => {
                return {id: d["study id"], label: d["study citation"]};
            })
            .value();
    }

    @computed get metricIdChoices() {
        return _.chain(this.dataset.rob)
            .uniqBy("metric_id")
            .map(d => {
                return {id: d["metric_id"], label: d["metric_id"]};
            })
            .value();
    }

    scoreIdChoices(studyId, metricId) {
        return _.chain(this.dataset.rob)
            .filter(d => d["study_id"] == studyId && d["metric_id"] == metricId)
            .uniqBy("score_id")
            .map(d => {
                return {id: d["score_id"], label: d["score_id"]};
            })
            .value();
    }

    getCustomized(rowIdx, colKey) {
        return _.find(this.workingSettings.rows[rowIdx].customized, d => d.key == colKey);
    }

    getDefaultCustomized(row, col) {
        if (col.attribute == "rob_score") {
            let val = this.scoreIdChoices(row.id, col.metric_id)[0];
            return val == null
                ? {key: col.key, score_id: undefined}
                : {key: col.key, score_id: val["id"]};
        }
        return {key: col.key, html: "<p></p>"};
    }

    getDataSelection(type, id) {
        switch (type) {
            case "study":
                return _.filter(this.dataset.data, d => d["study id"] == id);
            default:
                return [];
        }
    }

    concatDataSelection(data, attribute) {
        switch (attribute) {
            case "study_name":
                return _.chain(data)
                    .map(d => d["study citation"])
                    .uniq()
                    .join("; ")
                    .value();
            case "species_strain_sex":
                return _.chain(data)
                    .map(d => d["animal description"])
                    .uniq()
                    .join("; ")
                    .value();
            case "doses":
                return _.chain(data)
                    .map(d => d["doses"])
                    .uniq()
                    .join("; ")
                    .value();
        }
    }

    getCellContent(rowIdx, colIdx) {
        // TODO return as object with properties "html" and "color", for consistency?
        let row = this.workingSettings.rows[rowIdx],
            col = this.workingSettings.columns[colIdx],
            customized = this.getCustomized(rowIdx, col.key);
        switch (col.attribute) {
            case "rob_score":
                if (customized == null) {
                    let data = _.filter(
                            this.dataset.rob,
                            d =>
                                d["study_id"] == row.id &&
                                d["metric_id"] == col.metric_id &&
                                _.isNil(d["content_type_id"])
                        ),
                        judgement = data.length ? data[0]["score_score"] : -1;
                    // TODO get actual thing
                    return judgement;
                } else {
                    let data = _.filter(
                            this.dataset.rob,
                            d => d["score_id"] == customized.score_id
                        ),
                        judgement = data.length ? data[0]["score_score"] : -1;
                    return judgement;
                }
            case "study_name":
            case "species_strain_sex":
            case "doses":
                if (customized == null) {
                    let data = this.getDataSelection(row.type, row.id);
                    return this.concatDataSelection(data, col.attribute);
                } else {
                    return customized.html;
                }
            case "free_html":
                return customized == null ? null : customized.html;
            default:
                return null;
        }
    }

    @action.bound setEditColumnIndex(idx) {
        this.editColumnIndex = idx;
        this.setStagedEdits();
    }
    @action.bound setEditRowIndex(idx) {
        this.editRowIndex = idx;
        this.setStagedEdits();
    }

    @action.bound fetchData() {
        if (this.hasData || this.isFetchingData) {
            return;
        }
        const url = constants.dataUrl(
            this.table.table_type,
            this.settings.data_source,
            this.table.assessment
        );
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

    // row updates
    @action.bound createRow() {
        const rows = this.rowIdChoices;
        if (rows.length > 0) {
            const item = constants.createNewRow(rows[0].id);
            this.settings.rows.push(item);
            if (this.stagedEdits != null) {
                this.stagedEdits.rows.push(item);
            }
        }
    }

    @action.bound moveRow(rowIdx, offset) {
        if (rowIdx + offset >= 0 && rowIdx + offset < this.numRows) {
            const r1 = this.settings.rows[rowIdx],
                r2 = this.settings.rows[rowIdx + offset];
            this.settings.rows[rowIdx] = r2;
            this.settings.rows[rowIdx + offset] = r1;
            this.stagedEdits.rows[rowIdx] = r2;
            this.stagedEdits.rows[rowIdx + offset] = r1;
            this.editRowIndex = rowIdx + offset;
        }
    }
    @action.bound deleteRow(rowIdx) {
        this.settings.rows.splice(rowIdx, 1);
        this.resetStagedEdits();
    }

    // column updates
    @action.bound createColumn() {
        const item = constants.createNewColumn();
        this.settings.columns.push(item);
        if (this.stagedEdits != null) {
            this.stagedEdits.columns.push(item);
        }
    }

    @action.bound moveColumn(colIdx, offset) {
        if (colIdx + offset >= 0 && colIdx + offset < this.numColumns) {
            const c1 = this.settings.columns[colIdx],
                c2 = this.settings.columns[colIdx + offset];
            this.settings.columns[colIdx] = c2;
            this.settings.columns[colIdx + offset] = c1;
            this.stagedEdits.columns[colIdx] = c2;
            this.stagedEdits.columns[colIdx + offset] = c1;
            this.editColumnIndex = colIdx + offset;
        }
    }
    @action.bound deleteColumn(columnIdx) {
        this.settings.columns.splice(columnIdx, 1);
        // TODO remove customized using column key
        this.resetStagedEdits();
    }

    // inject new settings from parent object
    @action.bound updateSettings(settings) {
        this.settings = settings;
    }
}

export default StudyOutcomeTableStore;
