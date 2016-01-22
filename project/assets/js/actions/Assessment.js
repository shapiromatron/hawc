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

function releaseContent(){
    return {
        type: types.AS_RELEASE,
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

export function releaseAssessment(id){
    return (dispatch) => {
        dispatch(releaseContent());
    };
}
