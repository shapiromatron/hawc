import fetch from 'isomorphic-fetch';
import _ from 'underscore';
import * as types from 'robVisual/constants/ActionTypes';
import h from 'robVisual/utils/helpers';

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
        return fetch(h.getTestUrl(state.config.apiUrl, state.config.endpoint_effect_url), h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveEffects(json)))
            .catch((ex) => console.error('Effect parsing failed', ex));
    };
}
