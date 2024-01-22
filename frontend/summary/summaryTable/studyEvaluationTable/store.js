import _ from "lodash";
import {action, autorun, computed, observable} from "mobx";
import RiskOfBiasScore from "riskofbias/RiskOfBiasScore";
import {renderRiskOfBiasDisplay} from "riskofbias/robTable/components/RiskOfBiasDisplay";
import HAWCModal from "shared/utils/HAWCModal";
import h from "shared/utils/helpers";
import Study from "study/Study";

import * as constants from "./constants";

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
            if (col.attribute == constants.COL_ATTRIBUTE.ROB.id) {
                delete col.metric_id;
            }
            if (value.attribute == constants.COL_ATTRIBUTE.ROB.id) {
                let metric = this.metricIdChoices[0];
                col.metric_id = metric == null ? undefined : metric["id"];
            }
            if (col.attribute == constants.COL_ATTRIBUTE.ANIMAL_GROUP_DOSES.id) {
                delete col.dose_unit;
            }
            if (value.attribute == constants.COL_ATTRIBUTE.ANIMAL_GROUP_DOSES.id) {
                col.dose_unit = this.doseUnitChoices[0]["id"];
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
    rowTypeChoices(row) {
        // filter type choices down to whats achievable with the current row type/id
        let choices = constants.rowTypeChoices[this.settings.data_source],
            currentIndex = _.findIndex(choices, c => c.id == row.type),
            endIndex = _.findIndex(
                choices,
                c =>
                    _.find(
                        this.dataset.data,
                        d => d["type"] == c.id && d[`${row.type}_id`] == row.id
                    ) == null,
                currentIndex + 1
            );
        return endIndex == -1 ? choices : choices.slice(0, endIndex);
    }
    rowIdChoices(row, type) {
        const data = this.getDataSelection(row.type, row.id);
        switch (type) {
            case constants.ROW_TYPE.STUDY.id:
                return _.chain(this.dataset.data)
                    .filter(d => d["type"] == data["type"])
                    .uniqBy("study_id")
                    .sortBy("study_short_citation")
                    .map(d => {
                        return {id: d["study_id"], label: d["study_short_citation"]};
                    })
                    .value();
            case constants.ROW_TYPE.EXPERIMENT.id:
                return _.chain(this.dataset.data)
                    .filter(d => d["type"] == data["type"] && d["study_id"] == data["study_id"])
                    .uniqBy("experiment_id")
                    .sortBy("experiment_name")
                    .map(d => {
                        return {id: d["experiment_id"], label: d["experiment_name"]};
                    })
                    .value();
            case constants.ROW_TYPE.ANIMAL_GROUP.id:
                return _.chain(this.dataset.data)
                    .filter(
                        d =>
                            d["type"] == data["type"] && d["experiment_id"] == data["experiment_id"]
                    )
                    .uniqBy("animal_group_id")
                    .sortBy("animal_group_name")
                    .map(d => {
                        return {id: d["animal_group_id"], label: d["animal_group_name"]};
                    })
                    .value();
        }
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
                    ),
                    domainSettings = _.find(
                        this.robSettings.domains,
                        s => s["id"] == metricSettings["domain_id"]
                    );
                return {
                    id: d["metric_id"],
                    label: metricSettings["use_short_name"]
                        ? metricSettings["short_name"]
                        : metricSettings["name"],
                    domainSortOrder: domainSettings["sort_order"],
                    metricSortOrder: metricSettings["sort_order"],
                };
            })
            .sortBy(["domainSortOrder", "metricSortOrder"])
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
    @computed get doseUnitChoices() {
        let choices = _.chain(this.dataset.data)
            .filter(d => d["type"] == constants.ROW_TYPE.STUDY.id)
            .map(d => _.keys(d[constants.COL_ATTRIBUTE.ANIMAL_GROUP_DOSES.id]))
            .flatten()
            .uniq()
            .map(d => {
                return {id: d, label: d};
            })
            .value();
        return [{id: "", label: "---"}, ...choices];
    }
    getDefaultColumnLabel(col) {
        switch (col.attribute) {
            case constants.COL_ATTRIBUTE.ROB.id:
                return _.find(this.metricIdChoices, c => c.id == col.metric_id).label;
            case constants.COL_ATTRIBUTE.ANIMAL_GROUP_DOSES.id:
                return col.dose_unit == "" ? "Doses" : `Doses (${col.dose_unit})`;
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
        return col.attribute == constants.COL_ATTRIBUTE.ROB.id
            ? {key: col.key, score_id: -1}
            : {key: col.key, html: this.getDefaultCellContent(row, col).html};
    }

    // cell content
    getDataSelection(type, id) {
        return _.find(this.dataset.data, d => d["type"] == type && d["id"] == id);
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
    getDefaultCellContent(row, col) {
        switch (col.attribute) {
            case constants.COL_ATTRIBUTE.ROB.id: {
                let data = this.getDataSelection(row.type, row.id),
                    robData = this.getRobSelection(data["study_id"], col.metric_id),
                    judgment = robData.length ? robData[0]["score_score"] : -1;
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
            case constants.COL_ATTRIBUTE.STUDY_SHORT_CITATION.id: {
                let data = this.getDataSelection(row.type, row.id),
                    text = data[col.attribute];
                return {
                    html: `<p><a href="/study/${data["study_id"]}" rel="noopener noreferrer" target="_blank">${text}</a></p>`,
                };
            }
            case constants.COL_ATTRIBUTE.ANIMAL_GROUP_DOSES.id: {
                let data = this.getDataSelection(row.type, row.id),
                    doses = data[col.attribute];
                if (col.dose_unit == "") {
                    let text = _.chain(_.entries(doses))
                        .map(([k, v]) =>
                            _.join(
                                _.map(v, _v => `${_v} ${k}`),
                                "; "
                            )
                        )
                        .join("; ");
                    return {html: `<p>${text}</p>`};
                } else {
                    let text = _.join(doses[col.dose_unit], "; ");
                    return {html: `<p>${text}</p>`};
                }
            }
            case constants.COL_ATTRIBUTE.FREE_HTML.id:
                return {html: "<p></p>"};
            default: {
                let data = this.getDataSelection(row.type, row.id),
                    text = data[col.attribute];
                return {html: `<p>${text}</p>`};
            }
        }
    }
    getCustomCellContent(attribute, customized) {
        switch (attribute) {
            case constants.COL_ATTRIBUTE.ROB.id: {
                let robData = this.getRobSelection(null, null, customized.score_id),
                    judgment = robData.length ? robData[0]["score_score"] : -1;
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
            default:
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
        const data = _.find(this.dataset.data, d => d["type"] == constants.ROW_TYPE.STUDY.id),
            item = constants.createNewRow(data["id"]);
        this.settings.rows.push(item);
        if (this.stagedEdits != null) {
            this.stagedEdits.rows.push(item);
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
            customized = this.getCustomized(rowIdx, col.key),
            data = this.getDataSelection(row.type, row.id);
        if (col.attribute == constants.COL_ATTRIBUTE.ROB.id) {
            let scoreId = customized == null ? null : customized.score_id,
                selection = this.getRobSelection(data["study_id"], col.metric_id, scoreId);

            if (!selection.length) {
                return null;
            }

            let score = selection[0],
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
            return () => this.displayRobAsModal(_.extend({}, scoreData, robData), data, config);
        } else if (col.attribute == constants.COL_ATTRIBUTE.STUDY_SHORT_CITATION.id) {
            return () => Study.displayAsModal(data["study_id"]);
        }
    }
    displayRobAsModal(robData, data, config) {
        var modal = new HAWCModal(),
            title = `<h4><a target="_blank" href="/study/${data["study_id"]}">${
                data["study_short_citation"]
            }</a>${robData["label"] ? `: ${robData["label"]}` : ""}</h4>`,
            $content = $('<div class="container-fluid">');

        window.setTimeout(function () {
            renderRiskOfBiasDisplay(
                RiskOfBiasScore.format_for_react([new RiskOfBiasScore(null, robData)], config),
                $content[0]
            );
        }, 200);

        modal.addHeader(title).addFooter("").addBody($content).show({maxWidth: 1000});
    }
}

export default StudyEvaluationTableStore;
