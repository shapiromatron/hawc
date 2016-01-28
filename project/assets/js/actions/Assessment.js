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
        type: types.AS_RECEIVE_OBJECT,
        item,
    };
}

function releaseSelected(){
    return {
        type: types.AS_RELEASE,
    };
}

export function fetchObjectIfNeeded(id){
    return (dispatch, getState) => {
        let state = getState();
        console.log(state)
        if (state.assessment.isFetching) return;
        dispatch(requestContent());
        return fetch(h.getAssessmentApiUrl(state.config), h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveObject(json)))
            .catch((ex) => console.error('Assessment parsing failed', ex));
    };
}

export function releaseAssessment(id){
    return (dispatch) => {
        dispatch(releaseSelected());
    };
}

export function selectObject(id){
    return {
        type: types.AS_SELECT,
        id,
    };
}
