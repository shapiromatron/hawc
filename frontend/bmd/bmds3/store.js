import _ from "lodash";
import {action, computed, observable, toJS} from "mobx";

import $ from "$";

import Endpoint from "../../animal/Endpoint";
import h from "../../shared/utils/helpers";
import {bmrLabel, doseDropOptions, getLabel} from "./utils";

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
                this.settings = data.inputs;
                this.endpoint = new Endpoint(data.endpoint);
                this.endpoint.doseUnits.activate(data.inputs.dose_units_id);
                this.inputOptions = data.input_options;
                this.outputs = data.outputs;
                this.errors = data.errors;
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
                inputs: toJS(this.settings),
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
                            this.outputs = data.outputs;
                            this.errors = data.errors;
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
}

export default Bmd3Store;
