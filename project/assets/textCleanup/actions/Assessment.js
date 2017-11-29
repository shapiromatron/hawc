import fetch from 'isomorphic-fetch';
import _ from 'lodash';

import * as types from 'textCleanup/constants/ActionTypes';
import h from 'textCleanup/utils/helpers';


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

function selectObject(object){
    return {
        type: types.AS_SELECT,
        object,
    };
}

export function makeAssessmentActive(id){
    return (dispatch, getState) => {
        let state = getState();
        if (state.assessment.isFetching) return;
        let item = _.find(state.assessment.items, {id});
        if (item){
            dispatch(selectObject(item));
        } else {
            dispatch(requestContent());
            return fetch(h.getAssessmentApiUrl(state.config), h.fetchGet)
                .then((response) => response.json())
                .then((json) => dispatch(receiveObject(json)))
                .then((json) => dispatch(selectObject(json.item)))
                .catch((ex) => console.error('Assessment parsing failed', ex));
        }};
}
