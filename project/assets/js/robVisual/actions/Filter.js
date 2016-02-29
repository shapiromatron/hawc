import fetch from 'isomorphic-fetch';
import * as types from 'robVisual/constants/ActionTypes';
import h from 'robVisual/utils/helpers';

function receiveError(error){
    return {
        type: types.RECEIVE_ERROR,
        error,
    };
}

export function formatError(error){
    return (dispatch) => {
        error = h.formatErrors(error);
        dispatch(receiveError(error));
    };

}

export function clearErrors(){
    return {
        type: types.CLEAR_ERRORS,
    };
}

function requestEffects(){
    return {
        type: types.REQUEST_EFFECTS,
    };
}

function receiveEffects(effects){
    return {
        type: types.RECEIVE_EFFECTS,
        effects,
    };
}

export function fetchEffects(){
    return (dispatch, getState) => {
        let state = getState();
        if (state.isFetchingEffects) return;
        dispatch(requestEffects());
        return fetch(h.getTestUrl(state.config.host, state.config.endpoint_effect_url), h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveEffects(json)))
            .catch((ex) => console.error('Effect parsing failed', ex));
    };
}

export function selectEffects(effects){
    return {
        type: types.SELECT_EFFECTS,
        effects,
    };
}

function requestRobScores(){
    return {
        type: types.REQUEST_ROB_SCORES,
    };
}

function receiveRobScores(robScores){
    return {
        type: types.RECEIVE_ROB_SCORES,
        robScores,
    };
}

export function fetchRobScores(){
    return (dispatch, getState) => {
        let state = getState();
        if (state.isFetchingRobScores) return;
        dispatch(requestRobScores());
        return fetch(h.getTestUrl(state.config.host, state.config.study_score_url), h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveRobScores(json)))
            .catch((ex) => console.error('Effect parsing failed', ex));
    };
}

export function setScoreThreshold(threshold){
    return {
        type: types.SET_ROB_THRESHOLD,
        threshold,
    };
}

function requestEndpoints(){
    return {
        type: types.REQUEST_ENDPOINTS,
    };
}

function receiveEndpoints(endpoints){
    return {
        type: types.RECEIVE_ENDPOINTS,
        endpoints,
    };
}

export function fetchEndpoints(ids){
    return (dispatch, getState) => {
        let state = getState(),
            effects = state.filter.selectedEffects;
        if (state.isFetchingEndpoints) return;
        dispatch(requestEndpoints());
        return fetch(h.getEndpointsUrl(state.config, ids, effects), h.fetchGet)
            .then((response) => {
                if (response.ok){
                    response.json()
                        .then((json) => dispatch(receiveEndpoints(json)));
                } else {
                    response.json()
                        .then((json) => dispatch(receiveError(h.formatErrors(json.detail))));
                }
            })
            .catch((ex) => {
                console.error('Effect parsing failed', ex);
            });
    };
}
