import $ from "$";
import fetch from "isomorphic-fetch";

import h from "riskofbias/robTable/utils/helpers";

import * as types from "bmd/constants";

import Endpoint from "animal/Endpoint";

var showModal = function(name) {
        return $("#" + name).modal("show");
    },
    receiveEndpoint = function(endpoint) {
        return {
            type: types.RECEIVE_ENDPOINT,
            endpoint,
        };
    },
    receiveSession = function(settings) {
        return {
            type: types.RECEIVE_SESSION,
            settings,
        };
    },
    fetchEndpoint = function(id) {
        return (dispatch, getState) => {
            const url = Endpoint.get_api_url(id);
            return fetch(url, h.fetchGet)
                .then(response => response.json())
                .then(json => dispatch(receiveEndpoint(new Endpoint(json))))
                .catch(ex => console.error("Endpoint parsing failed", ex));
        };
    },
    fetchSessionSettings = function(session_url) {
        return (dispatch, getState) => {
            return fetch(session_url, h.fetchGet)
                .then(response => response.json())
                .then(json => dispatch(receiveSession(json)))
                .catch(ex => console.error("Endpoint parsing failed", ex));
        };
    },
    changeUnits = function(doseUnits) {
        return {
            type: types.CHANGE_UNITS,
            doseUnits,
        };
    },
    selectModel = function(modelIndex) {
        return {
            type: types.SELECT_MODEL,
            modelIndex,
        };
    },
    selectOutput = function(models) {
        return {
            type: types.SELECT_OUTPUT,
            models,
        };
    },
    setHoverModel = function(model) {
        return {
            type: types.HOVER_MODEL,
            model,
        };
    },
    showOptionModal = function(modelIndex) {
        return (dispatch, getState) => {
            // create a new noop Promise to chain events
            return new Promise((res, rej) => {
                res();
            })
                .then(() => dispatch(selectModel(modelIndex)))
                .then(() => showModal(types.OPTION_MODAL_ID));
        };
    },
    selectBmr = function(bmrIndex) {
        return {
            type: types.SELECT_BMR,
            bmrIndex,
        };
    },
    showBmrModal = function(bmrIndex) {
        return (dispatch, getState) => {
            // create a new noop Promise to chain events
            return new Promise((res, rej) => {
                res();
            })
                .then(() => dispatch(selectBmr(bmrIndex)))
                .then(() => showModal(types.BMR_MODAL_ID));
        };
    },
    showOutputModal = function(models) {
        return (dispatch, getState) => {
            // create a new noop Promise to chain events
            return new Promise((res, rej) => {
                res();
            })
                .then(() => dispatch(selectOutput(models)))
                .then(() => showModal(types.OUTPUT_MODAL_ID));
        };
    },
    setErrors = function(validationErrors) {
        return {
            type: types.VALIDATE,
            validationErrors,
        };
    },
    execute_start = function() {
        return {
            type: types.EXECUTE_START,
        };
    },
    execute_stop = function() {
        return {
            type: types.EXECUTE_STOP,
        };
    },
    execute = function() {
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
    },
    validate = function(state) {
        let errs = [];
        if (state.bmd.bmrs.length === 0) {
            errs.push("At least one BMR setting is required.");
        }
        if (state.bmd.modelSettings.length === 0) {
            errs.push("At least one model is required.");
        }
        return errs;
    },
    tryExecute = function() {
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
    },
    getExecuteStatus = function() {
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
    },
    getExecutionResults = function() {
        return (dispatch, getState) => {
            let url = getState().config.session_url;
            return new Promise((res, rej) => {
                res();
            })
                .then(() => dispatch(fetchSessionSettings(url)))
                .then(() => dispatch(execute_stop()))
                .then(() => $("#tabs a:eq(1)").tab("show"));
        };
    },
    toggleVariance = function() {
        return {
            type: types.TOGGLE_VARIANCE,
        };
    },
    addAllModels = function(settings) {
        return {
            type: types.ADD_ALL_MODELS,
        };
    },
    removeAllModels = function(settings) {
        return {
            type: types.REMOVE_ALL_MODELS,
        };
    },
    createModel = function(modelIndex) {
        return {
            type: types.CREATE_MODEL,
            modelIndex: parseInt(modelIndex),
        };
    },
    updateModel = function(values) {
        return {
            type: types.UPDATE_MODEL,
            values,
        };
    },
    deleteModel = function() {
        return {
            type: types.DELETE_MODEL,
        };
    },
    createBmr = function() {
        return {
            type: types.CREATE_BMR,
        };
    },
    updateBmr = function(values) {
        return {
            type: types.UPDATE_BMR,
            values,
        };
    },
    deleteBmr = function() {
        return {
            type: types.DELETE_BMR,
        };
    },
    setSelectedModel = function(model_id, notes) {
        return {
            type: types.SET_SELECTED_MODEL,
            model_id,
            notes,
        };
    },
    saveSelectedModel = function(model_id, notes) {
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
    },
    applyLogic = function() {
        return {
            type: types.APPLY_LOGIC,
        };
    };

export {fetchEndpoint};
export {fetchSessionSettings};
export {changeUnits};
export {showOptionModal};
export {showBmrModal};
export {showOutputModal};
export {setHoverModel};
export {tryExecute};
export {toggleVariance};
export {addAllModels};
export {removeAllModels};
export {createModel};
export {updateModel};
export {deleteModel};
export {createBmr};
export {updateBmr};
export {deleteBmr};
export {selectModel};
export {applyLogic};
export {setSelectedModel};
export {saveSelectedModel};
