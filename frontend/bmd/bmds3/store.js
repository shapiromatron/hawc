import {action, computed, observable} from "mobx";

import $ from "$";

import Endpoint from "../../animal/Endpoint";
import h from "../../shared/utils/helpers";
import {bmrLabel, doseDropOptions, getLabel} from "./utils";

class Bmd3Store {
    constructor(config) {
        this.config = config;
    }
    @observable endpoint = null;

    // INPUT SETTINGS CONFIG
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
        return getLabel(this.settings.variance_model, this.varianceModelChoices);
    }
    @computed get bmrText() {
        return bmrLabel(this.inputOptions.dtype, this.settings.bmr_type, this.settings.bmr_value);
    }
    @action.bound
    changeSetting(key, value) {
        this.settings[key] = value;
        if (key === "dose_units_id") {
            this.endpoint.doseUnits.activate(value);
        }
    }

    // FETCH SESSION INFO
    @observable hasSessionLoaded = false;
    @action.bound
    fetchSession() {
        const url = this.config.session_url;
        this.hasSessionLoaded = false;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(data => {
                this.settings = data.inputs;
                this.endpoint = new Endpoint(data.endpoint);
                this.endpoint.doseUnits.activate(data.inputs.dose_units_id);
                this.inputOptions = data.input_options;
                this.hasSessionLoaded = true;
            })
            .catch(ex => console.error("Session fetching failed", ex));
    }

    // EXECUTION STATE
    @observable isExecuting = false;
    @action.bound
    saveAndExecute() {
        this.isExecuting = true;
        window.setTimeout(() => {
            this.isExecuting = false;
            $(".bmd-results-tab").click();
        }, 3000);
    }
}

export default Bmd3Store;
