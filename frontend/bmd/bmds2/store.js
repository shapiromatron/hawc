import _ from "lodash";
import {action, autorun, computed, observable} from "mobx";

import h from "shared/utils/helpers";
import Endpoint from "animal/Endpoint";
import {applyRecommendationLogic} from "bmd/common/recommendationLogic";
import {BMR_MODAL_ID, OPTION_MODAL_ID, OUTPUT_MODAL_ID} from "./constants";

class Bmd2Store {
    constructor(config) {
        this.config = config;
    }

    @observable errors = [];
    @observable hasExecuted = false;
    @observable isReady = false;
    @observable endpoint = null;
    @observable dataType = null;
    @observable session = null;
    @observable doseUnits = null;
    @observable models = [];
    @observable modelSettings = [];
    @observable selectedModelOptionIndex = null;
    @observable selectedModelOption = null;
    @observable bmrs = [];
    @observable selectedBmrIndex = null;
    @observable selectedBmr = null;
    @observable allModelOptions = [];
    @observable allBmrOptions = null;
    @observable isExecuting = false;
    @observable validationErrors = [];
    @observable selectedOutputs = [];
    @observable hoverModel = null;
    @observable selectedModelId = null;
    @observable selectedModelNotes = "";
    @observable logic = [];

    // actions

    // fetch-settings
    @action.bound fetchEndpoint(id) {
        const url = `/ani/api/endpoint/${this.config.endpoint_id}/`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                const endpoint = new Endpoint(json);
                this.dataType = endpoint.data.data_type;
                // do endpoint last; this triggers other side effects
                this.endpoint = endpoint;
            })
            .catch(ex => console.error("Endpoint parsing failed", ex));
    }
    @action.bound fetchSessionSettings(callback) {
        const url = this.config.session_url;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(settings => {
                // add key-prop to each values dict for parameter
                _.each(settings.allModelOptions, d => _.each(d.defaults, (v, k) => (v.key = k)));

                // create model-settings
                // 1) only get the first bmr instance of the model
                // 2) add defaults based on the model name
                const modelSettingsMap = _.keyBy(settings.allModelOptions, "name");
                settings.models.forEach(d => (d.defaults = modelSettingsMap[d.name].defaults));

                const modelSettings = _.chain(settings.models)
                    .filter(d => d.bmr_id === 0)
                    .map(d => h.deepCopy(d))
                    .value();

                // set store features
                this.models = settings.models;
                this.modelSettings = modelSettings;
                this.bmrs = settings.bmrs;
                this.doseUnits = settings.dose_units;
                this.allModelOptions = settings.allModelOptions;
                this.allBmrOptions = _.keyBy(settings.allBmrOptions, "type");
                this.logic = settings.logic;
                this.hasExecuted = settings.is_finished;

                if (settings.selected_model) {
                    this.selectedModelId = settings.selected_model.model;
                    this.selectedModelNotes = settings.selected_model.notes;
                } else {
                    this._resetSelectedModel();
                }

                // do session last; this triggers other side effects
                this.session = settings;

                if (callback) {
                    callback();
                }
            })
            .catch(ex => console.error("Endpoint parsing failed", ex));
    }
    @action.bound _resetSelectedModel() {
        this.selectedModelId = null;
        this.selectedModelNotes = "";
    }
    @action.bound applyRecommendationLogic() {
        if (this.hasExecuted) {
            applyRecommendationLogic(this.logic, this.models, this.endpoint, this.doseUnits);
        }
        this.isReady = true;
    }
    autoApplyRecommendationLogic = autorun(() => {
        if (this.hasSession && this.hasEndpoint) {
            this.applyRecommendationLogic();
        }
    });

    // ui settings
    @action.bound showModal(name) {
        // wait until the modal element is rendered in the DOM before triggering show modal
        let waitedFor = 0;
        const waitInterval = 20,
            maxWait = 1000,
            selector = `#${name}`,
            tryShow = () => {
                waitedFor += waitInterval;
                if ($(selector).length > 0 && !$(selector).hasClass("in")) {
                    $(selector).modal("show");
                } else {
                    if (waitedFor < maxWait) {
                        setTimeout(tryShow, waitInterval);
                    }
                }
            };
        setTimeout(tryShow, waitInterval);
    }
    @action.bound showOptionModal(modelIndex) {
        this.selectedModelOptionIndex = modelIndex;
        this.selectedModelOption = this.modelSettings[modelIndex];
        this.showModal(OPTION_MODAL_ID);
    }
    @action.bound showBmrModal(index) {
        this.selectedBmrIndex = index;
        this.selectedBmr = this.bmrs[index];
        this.showModal(BMR_MODAL_ID);
    }
    @action.bound showOutputModal(models) {
        this.selectedOutputs = models;
        this.showModal(OUTPUT_MODAL_ID);
    }

    // settings tab - dataset
    @action.bound changeUnits(doseUnits) {
        this.doseUnits = doseUnits;
    }

    // settings tab - models
    @action.bound createModel(modelIndex) {
        const template = this.allModelOptions[modelIndex],
            newModel = Object.assign(h.deepCopy(template), {
                overrides: {},
            });
        this.modelSettings.push(newModel);
    }
    @action.bound addAllModels() {
        const newModels = _.map(this.allModelOptions, d =>
            Object.assign(h.deepCopy(d), {overrides: {}})
        );
        _.each(newModels, model => this.modelSettings.push(model));
    }
    @action.bound removeAllModels(settings) {
        this.modelSettings = [];
    }
    @action.bound toggleVariance() {
        this.modelSettings.forEach(model => {
            model.overrides.constant_variance = model.overrides.constant_variance === 0 ? 1 : 0;
        });
    }
    @action.bound updateModel(values) {
        this.modelSettings[this.selectedModelOptionIndex].overrides = values;
        this.selectedModelOptionIndex = null;
        this.selectedModelOption = null;
    }
    @action.bound deleteModel() {
        this.modelSettings.splice(this.selectedModelOptionIndex, 1);
        this.selectedModelOption = null;
        this.selectedModelOptionIndex = null;
    }

    // settings tab - bmr
    @action.bound createBmr() {
        this.bmrs.push(_.values(this.allBmrOptions)[0]);
    }
    @action.bound updateBmr(values) {
        this.bmrs[this.selectedBmrIndex] = values;
    }
    @action.bound deleteBmr() {
        this.bmrs.splice(this.selectedBmrIndex, 1);
        this.selectedBmrIndex = null;
        this.selectBmr = null;
    }

    // validation/execution
    @action.bound _validate() {
        let errors = [];
        if (this.bmrs.length === 0) {
            errors.push("At least one BMR setting is required.");
        }
        if (this.modelSettings.length === 0) {
            errors.push("At least one model is required.");
        }
        this.isExecuting = false;
        this.validationErrors = errors;
    }
    @action.bound _execute() {
        const {execute_url, csrf} = this.config,
            data = {
                dose_units: this.doseUnits,
                bmrs: this.bmrs,
                modelSettings: this.modelSettings,
            },
            payload = h.fetchPost(csrf, data, "POST");

        this.isExecuting = true;
        this.errors = [];
        fetch(execute_url, payload)
            .then(response => {
                if (!response.ok) {
                    this.errors = ["An error occurred."];
                }
                return response.json();
            })
            .then(() => setTimeout(() => this._getExecuteStatus()), 3000);
    }
    @action.bound tryExecute() {
        this._validate();
        if (this.validationErrors.length === 0) {
            this._resetSelectedModel();
            this._execute();
        }
    }
    @action.bound _getExecuteStatus() {
        const url = this.config.execute_status_url;
        fetch(url, h.fetchGet)
            .then(res => res.json())
            .then(res => {
                if (res.finished) {
                    this._getExecutionResults();
                } else {
                    setTimeout(() => this._getExecuteStatus(), 3000);
                }
            });
    }
    @action.bound _getExecutionResults() {
        const cb = () => {
            this.isExecuting = false;
            this.applyRecommendationLogic();
            $(".bmdResultsTab").click();
        };
        this.fetchSessionSettings(cb);
    }

    // outputs
    @action.bound setHoverModel(model) {
        this.hoverModel = model;
    }
    @action.bound saveSelectedModel(model_id, notes) {
        const url = this.config.selected_model_url,
            data = {model: model_id, notes};

        fetch(url, h.fetchPost(this.config.csrf, data, "POST")).then(() => {
            this.selectedModelId = model_id;
            this.selectedModelNotes = notes;
        });
    }

    @computed get hasEndpoint() {
        return this.endpoint !== null;
    }
    @computed get hasSession() {
        return this.session !== null;
    }
}

export default Bmd2Store;
