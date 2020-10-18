import _ from "lodash";
import fetch from "isomorphic-fetch";
import {action, autorun, computed, observable} from "mobx";

import h from "shared/utils/helpers";
import Endpoint from "animal/Endpoint";
import {apply_logic} from "./models/logic";

class Bmd2Store {
    constructor(config) {
        this.config = config;
    }

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
    @action.bound receiveSession(settings) {
        return {
            type: types.RECEIVE_SESSION,
            settings,
        };
    }
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
    @action.bound fetchSessionSettings() {
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

                const selectedModel = settings.selected_model || {model: null, notes: ""};

                // set store features
                this.models = settings.models;
                this.modelSettings = modelSettings;
                this.bmrs = settings.bmrs;
                this.doseUnits = settings.dose_units;
                this.allModelOptions = settings.allModelOptions;
                this.allBmrOptions = _.keyBy(settings.allBmrOptions, "type");
                this.selectedModelId = selectedModel.model;
                this.selectedModelNotes = selectedModel.notes;
                this.logic = settings.logic;
                this.hasExecuted = settings.is_finished;
                // do session last; this triggers other side effects
                this.session = settings;
            })
            .catch(ex => console.error("Endpoint parsing failed", ex));
    }
    @action.bound applyLogic() {
        apply_logic(this.logic, this.models, this.endpoint, this.doseUnits);
        this.isReady = true;
    }
    autoApplyLogic = autorun(() => {
        if (this.hasSession && this.hasEndpoint) {
            this.applyLogic();
        }
    });

    // ui settings
    @action.bound showModal(name) {
        return $("#" + name).modal("show");
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
    @action.bound selectModel(modelIndex) {
        this.selectedModelOptionIndex = modelIndex;
        this.selectedModelOption = this.modelSettings[modelIndex];
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
        // AJS TODO; content updates but doesn't persist on the UI
    }

    // TODO resume...
    @action.bound updateModel(values) {
        return {
            type: types.UPDATE_MODEL,
            values,
        };
    }
    @action.bound deleteModel() {
        return {
            type: types.DELETE_MODEL,
        };
    }

    @action.bound createBmr() {
        return {
            type: types.CREATE_BMR,
        };
    }
    @action.bound updateBmr(values) {
        return {
            type: types.UPDATE_BMR,
            values,
        };
    }
    @action.bound deleteBmr() {
        return {
            type: types.DELETE_BMR,
        };
    }

    @action.bound selectOutput(models) {
        return {
            type: types.SELECT_OUTPUT,
            models,
        };
    }
    @action.bound setHoverModel(model) {
        return {
            type: types.HOVER_MODEL,
            model,
        };
    }
    @action.bound showOptionModal(modelIndex) {
        return (dispatch, getState) => {
            // create a new noop Promise to chain events
            return new Promise((res, rej) => {
                res();
            })
                .then(() => dispatch(selectModel(modelIndex)))
                .then(() => showModal(types.OPTION_MODAL_ID));
        };
    }
    @action.bound selectBmr(bmrIndex) {
        return {
            type: types.SELECT_BMR,
            bmrIndex,
        };
    }
    @action.bound showBmrModal(bmrIndex) {
        return (dispatch, getState) => {
            // create a new noop Promise to chain events
            return new Promise((res, rej) => {
                res();
            })
                .then(() => dispatch(selectBmr(bmrIndex)))
                .then(() => showModal(types.BMR_MODAL_ID));
        };
    }
    @action.bound showOutputModal(models) {
        return (dispatch, getState) => {
            // create a new noop Promise to chain events
            return new Promise((res, rej) => {
                res();
            })
                .then(() => dispatch(selectOutput(models)))
                .then(() => showModal(types.OUTPUT_MODAL_ID));
        };
    }
    @action.bound setErrors(validationErrors) {
        return {
            type: types.VALIDATE,
            validationErrors,
        };
    }
    @action.bound execute_start() {
        return {
            type: types.EXECUTE_START,
        };
    }
    @action.bound execute_stop() {
        return {
            type: types.EXECUTE_STOP,
        };
    }
    @action.bound execute() {
        return (dispatch, getState) => {
            let state = getState(),
                url = state.config.execute_url,
                data = {
                    dose_units: state.bmd.doseUnits,
                    bmrs: state.bmd.bmrs,
                    modelSettings: state.bmd.modelSettings,
                };

            return new Promise((res, rej) => {
                res();
            })
                .then(() => dispatch(execute_start()))
                .then(() => {
                    fetch(url, h.fetchPost(state.config.csrf, data, "POST"))
                        .then(response => {
                            if (!response.ok) {
                                dispatch(setErrors(["An error occurred."]));
                            }
                            return response.json();
                        })
                        .then(() => setTimeout(() => dispatch(getExecuteStatus()), 3000));
                });
        };
    }
    @action.bound validate(state) {
        let errs = [];
        if (state.bmd.bmrs.length === 0) {
            errs.push("At least one BMR setting is required.");
        }
        if (state.bmd.modelSettings.length === 0) {
            errs.push("At least one model is required.");
        }
        return errs;
    }
    @action.bound tryExecute() {
        return (dispatch, getState) => {
            return new Promise((res, rej) => {
                res();
            })
                .then(() => {
                    let validationErrors = validate(getState());
                    dispatch(setErrors(validationErrors));
                })
                .then(() => {
                    let state = getState();
                    if (state.bmd.validationErrors.length === 0) {
                        dispatch(execute());
                    }
                });
        };
    }
    @action.bound getExecuteStatus() {
        return (dispatch, getState) => {
            let url = getState().config.execute_status_url;
            fetch(url, h.fetchGet)
                .then(res => res.json())
                .then(res => {
                    if (res.finished) {
                        dispatch(getExecutionResults());
                    } else {
                        setTimeout(() => dispatch(getExecuteStatus()), 3000);
                    }
                });
        };
    }
    @action.bound getExecutionResults() {
        return (dispatch, getState) => {
            let url = getState().config.session_url;
            return new Promise((res, rej) => {
                res();
            })
                .then(() => dispatch(fetchSessionSettings(url)))
                .then(() => dispatch(execute_stop()))
                .then(() => $("#tabs a:eq(1)").tab("show"));
        };
    }
    @action.bound setSelectedModel(model_id, notes) {
        return {
            type: types.SET_SELECTED_MODEL,
            model_id,
            notes,
        };
    }
    @action.bound saveSelectedModel(model_id, notes) {
        return (dispatch, getState) => {
            let state = getState(),
                url = state.config.selected_model_url,
                data = {
                    model: model_id,
                    notes,
                };

            return new Promise((res, rej) => {
                res();
            }).then(() => {
                fetch(url, h.fetchPost(state.config.csrf, data, "POST")).then(() =>
                    dispatch(setSelectedModel(model_id, notes))
                );
            });
        };
    }

    @computed get hasEndpoint() {
        return this.endpoint !== null;
    }
    @computed get hasSession() {
        return this.session !== null;
    }
}

export default Bmd2Store;
