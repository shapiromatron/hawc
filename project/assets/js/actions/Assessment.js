import fetch from 'isomorphic-fetch';
import * as types from '../constants/ActionTypes';
import h from '../utils/helpers';

function requestContent(){
    return {
        type: types.AS_REQUEST,
    };
}

function receiveObject(item){
    return {
        type: types.AS_RECIEVE_OBJECT,
        item,
    };
}

function removeObject(id) {
    return {
        type: types.AS_DELETE_OBJECT,
        id,
    };
}

export function fetchObjectIfNeeded(id){
    return (dispatch, getState) => {
        let state = getState();
        if (state.assessment.isFetching) return;
        dispatch(requestContent());
        return fetch(`${state.apiUrl}/${state.config.assessment}?assessment_id=${id}`, h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveObject(json)))
            .catch((ex) => console.error('Assessment parsing failed', ex));
    };
}

export function deleteObject(id, cb){
    cb = cb || h.noop;
    return (dispatch, getState) => {
        let state = getState(),
            opts = h.fetchDelete(state.config.csrf);
        return fetch(`${state.config.assessment}/?assessment_id=${id}/`, opts)
            .then(function(response){
                if (response.status === 204){
                    dispatch(removeObject(id));
                    cb(null);
                } else {
                    response.json()
                        .then((json) => cb(json));
                }
            })
            .catch((ex) => console.error('Analysis parsing failed', ex));
    };
}
