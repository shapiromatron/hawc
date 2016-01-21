import _ from 'underscore';
import fetch from 'isomorphic-fetch';
import * as types from '../constants/ActionTypes';
import h from '../utils/helpers';

function requestAssessment(){
    return {
        type: types.AS_REQUEST,
    };
}

function receiveObjects(json){
    return {
        type: types.AS_RECIEVE_OBJECTS,
        items: json,
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

function fetchObject(id){
    return (dispatch, getState) => {
        let state = getState();
        if (state.assessment.isFetching) return;
        dispatch(requestAssessment());
        return fetch(`${state.config.assessment}/?assessment_id=${id}/`, h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveObject(json)))
            .catch((ex) => console.error('Assessment parsing failed', ex));
    };
}

function setEditableObjects(object){
    return {
        type: types.AS_CREATE_EDIT_OBJECT,
        object,
    };
}

function receiveEditErrors(errors){
    return {
        type: types.AS_RECEIVE_EDIT_ERRORS,
        errors,
    };
}

function resetEditObject(){
    return {
        type: types.AS_RESET_EDIT_OBJECT,
    };
}

export function fetchObjectIfNeeded(id){
    return (dispatch, getState) => {
        let state = getState();
        if (state.assessment.isFetching) return;
        dispatch(requestAssessment());
        return fetch(`${state.apiUrl}/${state.config.assessment}?assessment_id=${id}`, h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveObject(json)))
            .catch((ex) => console.error('Assessment parsing failed', ex));
    };
}

export function patchObject(id, patch, cb) {
    cb = cb || h.noop;
    return (dispatch, getState) => {
        let state = getState(),
            opts = h.fetchPost(state.config.csrf, patch, 'PATCH');
        return fetch(`${state.config.assessment}/assessment_id=${id}/`, opts)
            .then(function(response){
                if (response.status === 200){
                    response.json()
                        .then((json) => dispatch(fetchObject(json.id)))
                        .then(cb())
                        .then(() => dispatch(resetEditObject()));
                } else {
                    response.json()
                        .then((json) => dispatch(receiveEditErrors(json)));
                }
            })
            .catch((ex) => console.error('Assessment parsing failed', ex));

    }

}

export function postObject(post, cb){
    cb = cb || noop
    return (dispatch, getState) => {
        let state = getState(),
            opts = h.fetchPost(state.config.csrf, post);
        return fetch(state.config.assessment, opts)
            .then((response) => {
                if (response.status === 200){
                    response.json()
                        .then((json) => dispatch(receiveObject(json)))
                        .then(cb())
                        .then(() => dispatch(resetEditObject()));
                } else {
                    response.json()
                        .then((json) => dispatch(receiveEditErrors(json)));
                }
            })
            .catch((ex) => console.error('Assessment parsing failed', ex));
    }
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
