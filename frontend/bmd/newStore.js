import _ from "lodash";
import fetch from "isomorphic-fetch";
import {action, computed, toJS, observable} from "mobx";

import h from "shared/utils/helpers";

class Bmd2Store {
    constructor(config) {
        this.config = config;
    }

    @observable hasSession = false;
    @observable hasEndpoint = false;
    @observable hasExecuted = false;
    @observable endpoint = null;
    @observable dataType = null;
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
    @observable logicApplied = false;

    // actions
    @action.bound showModal(name) {
        return $("#" + name).modal("show");
    }
    @action.bound receiveEndpoint(endpoint) {
        return {
            type: types.RECEIVE_ENDPOINT,
            endpoint,
        };
    }
    @action.bound receiveSession(settings) {
        return {
            type: types.RECEIVE_SESSION,
            settings,
        };
    }
    @action.bound fetchEndpoint(id) {
        return (dispatch, getState) => {
            const url = Endpoint.get_api_url(id);
            return fetch(url, h.fetchGet)
                .then(response => response.json())
                .then(json => dispatch(receiveEndpoint(new Endpoint(json))))
                .catch(ex => console.error("Endpoint parsing failed", ex));
        };
    }
    @action.bound fetchSessionSettings(session_url) {
        return (dispatch, getState) => {
            return fetch(session_url, h.fetchGet)
                .then(response => response.json())
                .then(json => dispatch(receiveSession(json)))
                .catch(ex => console.error("Endpoint parsing failed", ex));
        };
    }
    @action.bound changeUnits(doseUnits) {
        return {
            type: types.CHANGE_UNITS,
            doseUnits,
        };
    }
    @action.bound selectModel(modelIndex) {
        return {
            type: types.SELECT_MODEL,
            modelIndex,
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
    @action.bound toggleVariance() {
        return {
            type: types.TOGGLE_VARIANCE,
        };
    }
    @action.bound addAllModels(settings) {
        return {
            type: types.ADD_ALL_MODELS,
        };
    }
    @action.bound removeAllModels(settings) {
        return {
            type: types.REMOVE_ALL_MODELS,
        };
    }
    @action.bound createModel(modelIndex) {
        return {
            type: types.CREATE_MODEL,
            modelIndex: parseInt(modelIndex),
        };
    }
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
    @action.bound applyLogic() {
        return {
            type: types.APPLY_LOGIC,
        };
    }
}

export default Bmd2Store;
