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
    @action.bound changeSetting(key, value) {
        this.settings[key] = value;
        if (key === "dose_units_id") {
            this.endpoint.doseUnits.activate(value);
        }
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
    @observable outputs = null;
    @observable errors = null;
    @computed get hasErrors() {
        return _.isObject(this.errors) && _.size(this.errors) > 0;
    }
    @computed get hasOutputs() {
        return _.isObject(this.outputs) && _.size(this.outputs) > 0;
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
