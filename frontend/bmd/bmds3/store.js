import _ from "lodash";
import {action, computed, observable, toJS} from "mobx";

import $ from "$";

import Endpoint from "../../animal/Endpoint";
import h from "../../shared/utils/helpers";
import {
    addDoseUnitsToModels,
    bmrLabel,
    doseDropOptions,
    getLabel,
    getModelFromIndex,
    getPlotlyDrCurve,
} from "./utils";

class Bmd3Store {
    constructor(config) {
        this.config = config;
    }
    @observable endpoint = null;

    // FETCH SESSION
    @observable hasSessionLoaded = false;
    @action.bound fetchSession() {
        const url = this.config.session_url;
        this.hasSessionLoaded = false;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(data => {
                this.session = data;
                this.settings = data.inputs.settings;
                this.endpoint = new Endpoint(data.endpoint);
                this.endpoint.doseUnits.activate(data.inputs.settings.dose_units_id);
                this.inputOptions = data.input_options;
                addDoseUnitsToModels(data.outputs, data.inputs.settings.dose_units_id);
                this.date_executed = data.date_executed;
                this.outputs = data.outputs;
                this.errors = data.errors;
                this.selected = data.selected;
                const model = getModelFromIndex(data.selected.model_index, this.outputs.models);
                this.setSelectedModel(model);
                this.hasSessionLoaded = true;
            })
            .catch(ex => console.error("Session fetching failed", ex));
    }

    // INPUT SETTINGS
    @observable settings = null;
    @observable inputOptions = null;
    @computed get doseUnitChoices() {
        return this.endpoint.doseUnits.units.map(units => {
            return {id: units.id, label: units.name};
        });
    }
    @computed get bmrTypeChoices() {
        return this.inputOptions.bmr_types;
    }
    @computed get varianceModelChoices() {
        return this.inputOptions.dist_types || [];
    }
    @computed get doseDropChoices() {
        return doseDropOptions(this.inputOptions.dtype, this.endpoint);
    }
    @computed get isContinuous() {
        return this.inputOptions.dtype === "C";
    }
    @computed get isDichotomous() {
        return this.inputOptions.dtype === "D";
    }
    @computed get doseUnitsText() {
        return getLabel(this.settings.dose_units_id, this.doseUnitChoices);
    }
    @computed get variableModelText() {
        return _.isNumber(this.settings.variance_model)
            ? getLabel(this.settings.variance_model, this.varianceModelChoices)
            : "";
    }
    @computed get bmrText() {
        return bmrLabel(this.inputOptions.dtype, this.settings.bmr_type, this.settings.bmr_value);
    }
    @computed get bmrTypeLabel() {
        return _.find(this.inputOptions.bmr_types, d => d.id === this.settings.bmr_type).label;
    }
    @computed get distributionType() {
        return _.find(this.inputOptions.dist_types, d => d.id === this.settings.variance_model)
            .label;
    }
    @action.bound changeSetting(key, value) {
        this.settings[key] = value;
        if (key === "dose_units_id") {
            this.endpoint.doseUnits.activate(value);
        }
    }
    @computed get dosesArray() {
        const e = this.endpoint,
            doseUnitsId = this.settings.dose_units_id,
            doses = e.data.animal_group.dosing_regime.doses.filter(
                d => d.dose_units.id === doseUnitsId
            );
        return _.map(doses, "dose");
    }
    @computed get datasetTableProps() {
        const e = this.endpoint;
        let colNames, data;
        if (this.isDichotomous) {
            colNames = [
                `Dose (${this.doseUnitsText})`,
                "N",
                `Incidence (${e.data.response_units})`,
                "% Incidence",
            ];
            data = [
                this.dosesArray,
                _.map(e.data.groups, "n"),
                _.map(e.data.groups, "incidence"),
                _.map(e.data.groups, d => `${100 * _.round(d.incidence / d.n, 2)}%`),
            ];
        } else if (this.isContinuous) {
            colNames = [
                `Dose (${this.doseUnitsText})`,
                "N",
                `Response (${e.data.response_units})`,
                "Standard Deviation",
            ];
            data = [
                this.dosesArray,
                _.map(e.data.groups, "n"),
                _.map(e.data.groups, "response"),
                _.map(e.data.groups, "stdev"),
            ];
        } else {
            throw new Error("Unknown data type");
        }
        data = _.zip(...data); // transpose
        return {
            label: "",
            extraClasses: "table-sm table-striped text-right",
            colWidths: [25, 25, 25, 25],
            colNames,
            data,
        };
    }

    // EXECUTION STATE
    @observable isExecuting = false;
    @observable executionError = false;
    @action.bound saveAndExecute() {
        const url = this.config.session_url,
            payload = {
                action: "execute",
                inputs: {
                    version: 2,
                    dtype: this.inputOptions.dtype,
                    settings: toJS(this.settings),
                },
            },
            opts = h.fetchPost(this.config.csrf, payload, "PATCH");

        this.executionError = false;
        this.isExecuting = true;
        fetch(url, opts)
            .then(response => response.json())
            .then(response => {
                setTimeout(this.pollExecutionStatus, 5000);
            })
            .catch(ex => {
                console.error("Execute failed", ex);
                this.executionError = true;
            });
    }
    @action.bound pollExecutionStatus() {
        const url = this.session.url_execute_status,
            pollIsComplete = () => {
                fetch(url, h.fetchGet)
                    .then(response => response.json())
                    .then(data => {
                        if (data.is_finished) {
                            addDoseUnitsToModels(data.outputs, this.settings.dose_units_id);
                            this.date_executed = data.date_executed;
                            this.outputs = data.outputs;
                            this.errors = data.errors;
                            this.selected = data.selected;
                            this.isExecuting = false;
                            $(".bmd-results-tab").click();
                        } else {
                            setTimeout(pollIsComplete, 5000);
                        }
                    });
            };
        pollIsComplete();
    }

    // OUTPUTS
    @observable date_executed = null;
    @observable outputs = null;
    @observable errors = null;
    @computed get hasErrors() {
        return _.isObject(this.errors) && _.size(this.errors) > 0;
    }
    @computed get hasOutputs() {
        return _.isObject(this.outputs) && _.size(this.outputs) > 0;
    }
    @computed get pybmdsVersion() {
        return this.outputs.version.python;
    }
    @computed get executionDate() {
        return this.date_executed ? new Date(this.date_executed).toLocaleString() : null;
    }
    @computed get dataset() {
        return this.outputs.dataset;
    }

    // VISUALS
    @observable hoverModel = null;
    @action.bound setHoverModel(model) {
        this.hoverModel = model ? model : null;
    }
    @observable selectedModel = null;
    @action.bound setSelectedModel(model) {
        this.selectedModel = model ? model : null;
    }
    @computed get plottingRanges() {
        const data = this.drPlotDataset,
            yArr = _.flatten(data.customdata),
            minY = _.min(yArr),
            maxY = _.max(yArr),
            minX = _.min(data.x),
            maxX = _.max(data.x),
            buffX = Math.abs(maxX - minX) * 0.05,
            buffY = Math.abs(maxY - minY) * 0.05;
        return {
            x: [minX - buffX, maxX + buffX],
            y: this.isDichotomous ? [-0.05, 1.05] : [minY - buffY, maxY + buffY],
        };
    }
    @computed get drPlotLayout() {
        const e = this.endpoint,
            ranges = this.plottingRanges;
        return {
            autosize: true,
            legend: {
                yanchor: "top",
                y: 0.99,
                xanchor: "left",
                x: 0.05,
                bordercolor: "#efefef",
                borderwidth: 2,
            },
            margin: {l: 50, r: 5, t: 40, b: 40},
            showlegend: true,
            title: {
                text: e.data.name,
            },
            xaxis: {
                range: ranges.x,
                title: {
                    text: `Dose (${this.doseUnitsText})`,
                },
            },
            yaxis: {
                range: ranges.y,
                title: {
                    text: `Response (${e.data.response_units})`,
                },
            },
        };
    }
    @computed get drPlotDataset() {
        const groups = this.endpoint.data.groups,
            errorBars = {
                type: "data",
                symmetric: false,
                array: null,
                arrayminus: null,
            },
            data = {
                x: this.dosesArray,
                y: null,
                mode: "markers",
                type: "scatter",
                marker: {size: 10},
                error_y: errorBars,
                customdata: errorBars.bounds,
                hovertemplate:
                    "%{y:.3f} (%{customdata[0]:.3f}, %{customdata[1]:.3f})<extra></extra>",
                name: null,
            };
        if (this.isDichotomous) {
            data.y = groups.map(d => d.incidence / d.n);
            errorBars.array = groups.map(d => Math.max(0, d.upper_ci - d.incidence / d.n));
            errorBars.arrayminus = groups.map(d => Math.max(0, d.incidence / d.n - d.lower_ci));
            data.customdata = groups.map(d => [d.upper_ci, d.lower_ci]);
            data.name = "Fraction Affected ± 95% CI";
        } else if (this.isContinuous) {
            data.y = groups.map(d => d.response);
            errorBars.array = groups.map(d => Math.max(0, d.upper_ci - d.response));
            errorBars.arrayminus = groups.map(d => Math.max(0, d.response - d.lower_ci));
            data.customdata = groups.map(d => [d.upper_ci, d.lower_ci]);
            data.name = "Observed Mean ± 95% CI";
        } else {
            throw new Error("Unknown data type");
        }
        return data;
    }
    @computed get drPlotSelectedData() {
        if (!this.selectedModel) {
            return null;
        }
        return getPlotlyDrCurve(this.selectedModel, "#4a9f2f");
    }
    @computed get drPlotHover() {
        if (!this.hoverModel || this.hoverModel == this.selectedModel) {
            return null;
        }
        return getPlotlyDrCurve(this.hoverModel, "#DA2CDA");
    }
    @computed get drPlotModal() {
        if (!this.modalModel || this.modalModel == this.selectedModel) {
            return null;
        }
        return getPlotlyDrCurve(this.modalModel, "#DA2CDA");
    }

    // RESULTS
    @observable showModal = false;
    @observable modalModel = null;
    @action.bound enableModal(model) {
        this.modalModel = model;
        this.showModal = true;
    }
    @action.bound hideModal() {
        this.showModal = false;
        this.modalModel = null;
    }

    // SELECTED
    @observable selected = null;
    @observable showSelectedSaveNotification = false;
    @observable selectedError = false;
    @computed get selectedChoices() {
        const options = [{id: -1, label: "None (no model selected)"}];
        _.each(this.outputs.models, (model, index) => {
            options.push({id: index, label: model.name});
        });
        return options;
    }
    @action.bound changeSelectedNotes(value) {
        this.selected.notes = value;
    }
    @action.bound changeSelectedModel(value) {
        const model = getModelFromIndex(value, this.outputs.models);
        this.setSelectedModel(model);
        _.merge(this.selected, {
            model_index: value,
            bmr: this.bmrText,
            model: model ? model.name : "",
            bmdl: model ? model.results.bmdl : null,
            bmd: model ? model.results.bmd : null,
            bmdu: model ? model.results.bmdu : null,
        });
    }
    @action.bound handleSelectionSave() {
        const url = this.config.session_url,
            payload = {
                action: "select",
                selected: _.merge(toJS(this.selected), {version: 2}),
            },
            opts = h.fetchPost(this.config.csrf, payload, "PATCH");

        this.selectedError = false;
        this.showSelectedSaveNotification = false;
        fetch(url, opts)
            .then(response => response.json())
            .then(response => {
                this.showSelectedSaveNotification = true;
                setTimeout(() => {
                    this.showSelectedSaveNotification = false;
                }, 3000);
            })
            .catch(ex => {
                console.error("Selection failed", ex);
                this.selectedError = true;
            });
    }
}

export default Bmd3Store;
