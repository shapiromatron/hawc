import _ from "lodash";
import {action, autorun, computed, observable} from "mobx";

import * as constants from "./constants";
import h from "shared/utils/helpers";

import HAWCModal from "shared/utils/HAWCModal";
import Study from "study/Study";
import RiskOfBiasScore from "riskofbias/RiskOfBiasScore";
import {renderRiskOfBiasDisplay} from "riskofbias/robTable/components/RiskOfBiasDisplay";

class StudyEvaluationTableStore {
    @observable editMode = false;
    @observable settings = null;
    @observable robSettings = null;
    @observable isFetchingData = false;
    @observable isFetchingRob = false;
    @observable dataset = null;
    @observable datasetError = null;
    @observable editColumnIndex = null;
    @observable editIndex = null;

    @observable stagedEdits = null;
    @observable stagedDataSettings = null;

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
        this.stagedDataSettings = {
            data_source: table.content.data_source,
            published_only: table.content.published_only,
        };
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
            this.table.assessment,
            this.settings.published_only
        );
        this.datasetError = null;
        this.isFetchingData = true;
        fetch(url)
            .then(resp => {
                if (!resp.ok) {
                    resp.text().then(d => {
                        this.datasetError = d;
                    });
                    this.isFetchingData = false;
                    throw new Error("An error occurred in fetching data", resp);
                }
                return resp;
            })
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
    @action.bound updateStagedDataSettings(dataSettings) {
        _.assign(this.stagedDataSettings, _.pick(dataSettings, ["data_source", "published_only"]));
    }
    @action.bound removeSettings() {
        this.settings.rows = [];
        this.settings.columns = [];
        this.settings.subheaders = [];
    }
    @action.bound commitStagedDataSettings(removeSettings) {
        _.assign(this.settings, this.stagedDataSettings);
        if (removeSettings) {
            this.removeSettings();
        }
        this.resetStagedEdits();
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
        let col = this.stagedEdits.columns[colIdx],
            isDefaultLabel = col.label == this.getDefaultColumnLabel(col);
        if ("attribute" in value && col.attribute !== value.attribute) {
            if (col.attribute == "rob") {
                delete col.metric_id;
            } else if (value.attribute == "rob") {
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
        // update default column label if in use
        if (!("label" in value) && isDefaultLabel) {
            col.label = this.getDefaultColumnLabel(col);
        }
    }
    @action.bound commitStagedEdits() {
        _.assign(this.settings, this.stagedEdits);
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
        this.stagedEdits = _.cloneDeep(_.pick(this.settings, ["subheaders", "columns", "rows"]));
    }
    @computed get workingSettings() {
        return this.stagedEdits == null ? this.settings : this.stagedEdits;
    }

    // row attributes
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
                    label: d.score_label ? d.score_label : "No label",
                };
            })
            .unshift({id: -1, label: "Not measured"})
            .value();
    }
    getDefaultColumnLabel(col) {
        switch (col.attribute) {
            case "rob":
                return _.find(this.metricIdChoices, c => c.id == col.metric_id).label;
            default:
                return _.find(
                    constants.colAttributeChoices[this.settings.data_source],
                    c => c.id == col.attribute
                ).label;
        }
    }

    // customized rows
    getCustomized(rowIdx, colKey) {
        return _.find(this.workingSettings.rows[rowIdx].customized, d => d.key == colKey);
    }
    getDefaultCustomized(row, col) {
        return col.attribute == "rob"
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
    getRobSelection(studyId, metricId, scoreId) {
        if (scoreId != null) {
            return _.filter(this.dataset.rob, d => d["score_id"] == scoreId);
        }
        return _.filter(
            this.dataset.rob,
            d =>
                d["study_id"] == studyId &&
                d["metric_id"] == metricId &&
                _.isNil(d["content_type_id"])
        );
    }
    concatDataSelection(data, attribute) {
        switch (attribute) {
            case "study_short_citation":
                return _.chain(data)
                    .map(d => d["study citation"])
                    .uniq()
                    .join("; ")
                    .value();
            case "animal_group_description":
                return _.chain(data)
                    .map(d => d["animal description"])
                    .uniq()
                    .join("; ")
                    .value();
        }
    }
    getDefaultCellContent(row, col) {
        switch (col.attribute) {
            case "rob": {
                let data = this.getRobSelection(row.id, col.metric_id),
                    judgment = data.length ? data[0]["score_score"] : -1;
                return judgment == -1
                    ? constants.NM
                    : {
                          backgroundColor: this.robSettings.score_metadata.colors[judgment],
                          color: h.contrastingColor(
                              this.robSettings.score_metadata.colors[judgment]
                          ),
                          html: this.robSettings.score_metadata.symbols[judgment],
                      };
            }
            case "study_short_citation": {
                let data = this.getDataSelection(row.type, row.id),
                    text = this.concatDataSelection(data, col.attribute);
                return {
                    html: `<p><a href="/study/${row.id}" rel="noopener noreferrer" target="_blank">${text}</a></p>`,
                };
            }
            case "animal_group_description": {
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
            case "rob": {
                let data = this.getRobSelection(null, null, customized.score_id),
                    judgment = data.length ? data[0]["score_score"] : -1;
                return judgment == -1
                    ? constants.NM
                    : {
                          backgroundColor: this.robSettings.score_metadata.colors[judgment],
                          color: h.contrastingColor(
                              this.robSettings.score_metadata.colors[judgment]
                          ),
                          html: this.robSettings.score_metadata.symbols[judgment],
                      };
            }
            case "study_short_citation":
            case "animal_group_description":
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
        let last = [
                this.settings.subheaders[this.settings.subheaders.length - 1],
                this.stagedEdits == null
                    ? null
                    : this.stagedEdits.subheaders[this.stagedEdits.subheaders.length - 1],
            ],
            start = _.chain(last)
                .map(d => (d == null ? 1 : d.start + d.length))
                .max()
                .value(),
            item = constants.createNewSubheader(start);
        this.settings.subheaders.push(item);
        if (this.stagedEdits != null) {
            this.stagedEdits.subheaders.push(item);
        }
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

    // interactivity
    interactiveOnClick(rowIdx, colIdx) {
        let row = this.workingSettings.rows[rowIdx],
            col = this.workingSettings.columns[colIdx],
            customized = this.getCustomized(rowIdx, col.key);
        if (col.attribute == "rob") {
            let scoreId = customized == null ? null : customized.score_id,
                selection = this.getRobSelection(row.id, col.metric_id, scoreId);

            if (!selection.length) {
                return null;
            }

            let score = selection[0],
                study = this.getDataSelection("study", row.id)[0],
                config = {
                    display: "all",
                    isForm: false,
                    showStudyHeader: false,
                },
                scoreData = {
                    id: score["score_id"],
                    score: score["score_score"],
                    is_default: score["is_default"],
                    label: score["score_label"],
                    bias_direction: score["bias_direction"],
                    notes: score["score_notes"],
                    metric_id: score["metric_id"],
                    overridden_objects: [],
                    riskofbias_id: score["riskofbias_id"],
                },
                metric = _.find(this.robSettings.metrics, m => m["id"] == score["metric_id"]),
                domain = _.find(this.robSettings.domains, d => d["id"] == metric["domain_id"]),
                score_metadata = this.robSettings["score_metadata"],
                robData = {
                    assessment_id: this.robSettings.assessment_id,
                    score_description: score_metadata["choices"][score["score_score"]],
                    score_symbol: score_metadata["symbols"][score["score_score"]],
                    score_shade: score_metadata["colors"][score["score_score"]],
                    score_text_color: h.contrastingColor(
                        score_metadata["colors"][score["score_score"]]
                    ),
                    metric: {
                        id: metric["id"],
                        name: metric["name"],
                        description: metric["description"],
                        domain_id: metric["domain_id"],
                        responses: metric["responses"],
                        response_values: metric["response_values"],
                        default_response: metric["default_response"],
                        short_name: metric["short_name"],
                        use_short_name: metric["use_short_name"],
                        domain: {
                            id: domain["id"],
                            name: domain["name"],
                            description: domain["description"],
                            is_overall_confidence: domain["is_overall_confidence"],
                        },
                    },
                };
            return () => this.displayRobAsModal(_.extend({}, scoreData, robData), study, config);
        } else {
            return () => Study.displayAsModal(row.id);
        }
    }
    displayRobAsModal(data, study, config) {
        var modal = new HAWCModal(),
            title = `<h4><a target="_blank" href="/study/${study["study id"]}">${
                study["study citation"]
            }</a>${data["label"] ? `: ${data["label"]}` : ""}</h4>`,
            $content = $('<div class="container-fluid">');

        window.setTimeout(function() {
            renderRiskOfBiasDisplay(
                RiskOfBiasScore.format_for_react([new RiskOfBiasScore(null, data)], config),
                $content[0]
            );
        }, 200);

        modal
            .addHeader(title)
            .addFooter("")
            .addBody($content)
            .show({maxWidth: 1000});
    }
}

export default StudyEvaluationTableStore;
