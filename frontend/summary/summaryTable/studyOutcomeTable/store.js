import _ from "lodash";
import {action, autorun, computed, observable} from "mobx";

import * as constants from "./constants";

class StudyOutcomeTableStore {
    @observable editMode = false;
    @observable settings = null;
    @observable robSettings = null;
    @observable isFetchingData = false;
    @observable isFetchingRob = false;
    @observable dataset = null;
    @observable editColumnIndex = null;
    @observable editIndex = null;

    @observable stagedEdits = null;
    @observable stagedDataSource = null;

    @observable editingRow = false;
    @observable editingColumn = false;
    @observable editingSubheader = false;

    @computed get editing() {
        return this.editingSubheader || this.editingColumn || this.editingRow;
    }
    editingCell(rowIdx, colIdx) {
        return (
            (this.editingRow && this.editIndex == rowIdx) ||
            (this.editingColumn && this.editIndex == colIdx)
        );
    }

    constructor(editMode, table, editRootStore) {
        this.editMode = editMode;
        this.table = table;
        this.settings = table.content;
        this.stagedDataSource = table.content.data_source;
        this.editRootStore = editRootStore;
        this.fetchData();
        this.fetchRobSettings();
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

    // fetch data
    @action.bound fetchRobSettings() {
        const url = constants.robUrl(this.table.assessment);
        this.isFetchingRob = true;
        fetch(url)
            .then(d => d.json())
            .then(d => {
                this.robSettings = d;
                this.isFetchingRob = false;
            });
    }
    @action.bound fetchData() {
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
    @computed get isFetching() {
        return this.isFetchingData || this.isFetchingRob;
    }
    @computed get hasData() {
        return this.dataset !== null && this.dataset.data.length > 0;
    }

    // staged edits
    @action.bound updateStagedDataSource(dataSource) {
        this.stagedDataSource = dataSource;
    }
    @action.bound removeSettings() {
        this.settings.rows = [];
        this.settings.columns = [];
    }
    @action.bound commitStagedDataSource() {
        this.settings.data_source = this.stagedDataSource;
        this.removeSettings();
        this.fetchData();
    }
    @action.bound setEditSubheaderIndex(idx) {
        this.editingSubheader = true;
        this.editIndex = idx;
        this.setStagedEdits();
    }
    @action.bound setEditColumnIndex(idx) {
        this.editingColumn = true;
        this.editIndex = idx;
        this.setStagedEdits();
    }
    @action.bound setEditRowIndex(idx) {
        this.editingRow = true;
        this.editIndex = idx;
        this.setStagedEdits();
    }
    @action.bound updateStagedCell(rowIdx, colKey, value) {
        let row = this.stagedEdits.rows[rowIdx];
        row.customized = _.filter(row.customized, d => d.key != colKey);
        if (value != null) {
            row.customized.push(value);
        }
    }
    @action.bound updateStagedSubheader(shIdx, value) {
        let subheader = this.stagedEdits.subheaders[shIdx];
        if ("start" in value) {
            let {max} = this.getSubheaderBounds(shIdx),
                maxLength = max - value.start + 1;
            value.length = Math.min(subheader.length, maxLength);
        }
        _.assign(subheader, value);
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
        this.editingSubheader = false;
        this.editingColumn = false;
        this.editingRow = false;
        this.editIndex = null;
        this.stagedEdits = null;
    }
    @action.bound setStagedEdits() {
        this.stagedEdits = _.cloneDeep(this.settings);
    }
    @computed get workingSettings() {
        return this.stagedEdits == null ? this.settings : this.stagedEdits;
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

    // column attributes
    @computed get columnWidths() {
        const totalWidth = _.sumBy(this.workingSettings.columns, c => c.width);
        return _.map(this.workingSettings.columns, c => Math.round((c.width / totalWidth) * 100));
    }
    @computed get metricIdChoices() {
        return _.chain(this.dataset.rob)
            .uniqBy("metric_id")
            .map(d => {
                let metricSettings = _.find(
                    this.robSettings.metrics,
                    s => s["id"] == d["metric_id"]
                );
                return {
                    id: d["metric_id"],
                    label: metricSettings["use_short_name"]
                        ? metricSettings["short_name"]
                        : metricSettings["name"],
                };
            })
            .value();
    }
    scoreIdChoices(studyId, metricId) {
        return _.chain(this.dataset.rob)
            .filter(d => d["study_id"] == studyId && d["metric_id"] == metricId)
            .uniqBy("score_id")
            .map(d => {
                return {
                    id: d["score_id"],
                    label: `${d["score_label"] ? d["score_label"] : "No label"} (${
                        d["is_default"] ? "default score " : ""
                    }${d["score_id"]})`,
                };
            })
            .unshift({id: -1, label: "None"})
            .value();
    }

    // customized rows
    getCustomized(rowIdx, colKey) {
        return _.find(this.workingSettings.rows[rowIdx].customized, d => d.key == colKey);
    }
    getDefaultCustomized(row, col) {
        return col.attribute == "rob_score"
            ? {key: col.key, score_id: -1}
            : {key: col.key, html: this.getDefaultCellContent(row, col).html};
    }

    // cell content
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
    getDefaultCellContent(row, col) {
        switch (col.attribute) {
            case "rob_score": {
                let data = _.filter(
                        this.dataset.rob,
                        d =>
                            d["study_id"] == row.id &&
                            d["metric_id"] == col.metric_id &&
                            _.isNil(d["content_type_id"])
                    ),
                    judgment = data.length ? data[0]["score_score"] : -1;
                return judgment == -1
                    ? constants.NM
                    : {
                          color: this.robSettings.score_metadata.colors[judgment],
                          html: this.robSettings.score_metadata.symbols[judgment],
                      };
            }
            case "study_name":
            case "species_strain_sex":
            case "doses": {
                let data = this.getDataSelection(row.type, row.id),
                    text = this.concatDataSelection(data, col.attribute);
                return {html: `<p>${text}</p>`};
            }

            case "free_html":
                return {html: "<p></p>"};
        }
    }
    getCustomCellContent(attribute, customized) {
        switch (attribute) {
            case "rob_score": {
                let data = _.filter(this.dataset.rob, d => d["score_id"] == customized.score_id),
                    judgment = data.length ? data[0]["score_score"] : -1;
                return judgment == -1
                    ? constants.NM
                    : {
                          color: this.robSettings.score_metadata.colors[judgment],
                          html: this.robSettings.score_metadata.symbols[judgment],
                      };
            }
            case "study_name":
            case "species_strain_sex":
            case "doses":
            case "free_html":
                return {html: customized.html};
        }
    }
    getCellContent(rowIdx, colIdx) {
        let row = this.workingSettings.rows[rowIdx],
            col = this.workingSettings.columns[colIdx],
            customized = this.getCustomized(rowIdx, col.key);
        return customized == null
            ? this.getDefaultCellContent(row, col)
            : this.getCustomCellContent(col.attribute, customized);
    }

    // subheader updates
    getSubheaderBounds(shIdx) {
        let prev = shIdx > 0 ? this.settings.subheaders[shIdx - 1] : null,
            next =
                shIdx < this.settings.subheaders.length - 1
                    ? this.settings.subheaders[shIdx + 1]
                    : null,
            min = prev == null ? 1 : prev.start + prev.length,
            max = next == null ? Infinity : next.start - 1;
        return {min, max};
    }
    @action.bound createSubheader() {
        let last = this.settings.subheaders[this.settings.subheaders.length - 1],
            start = last == null ? 1 : last.start + last.length,
            item = constants.createNewSubheader(start);
        this.settings.subheaders.push(item);
    }
    @action.bound deleteSubheader(shIdx) {
        this.settings.subheaders.splice(shIdx, 1);
        this.resetStagedEdits();
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
        let move = rows => {
            const r1 = rows[rowIdx],
                r2 = rows[rowIdx + offset];
            rows[rowIdx] = r2;
            rows[rowIdx + offset] = r1;
        };
        if (rowIdx + offset >= 0 && rowIdx + offset < this.numRows) {
            move(this.settings.rows);
            move(this.stagedEdits.rows);
            this.editIndex = rowIdx + offset;
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
        let move = columns => {
            const c1 = columns[colIdx],
                c2 = columns[colIdx + offset];
            columns[colIdx] = c2;
            columns[colIdx + offset] = c1;
        };
        if (colIdx + offset >= 0 && colIdx + offset < this.numColumns) {
            move(this.settings.columns);
            move(this.stagedEdits.columns);
            this.editIndex = colIdx + offset;
        }
    }
    @action.bound deleteColumn(columnIdx) {
        let col = this.settings.columns.splice(columnIdx, 1)[0];
        _.forEach(this.settings.rows, r => _.remove(r.customized, c => c.key == col.key));
        this.resetStagedEdits();
    }

    // inject new settings from parent object
    @action.bound updateSettings(settings) {
        this.settings = settings;
    }
}

export default StudyOutcomeTableStore;
