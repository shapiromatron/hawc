import _ from 'underscore';
import 'babel-polyfill';

import * as types from 'textCleanup/constants/ActionTypes';
import h from 'textCleanup/utils/helpers';


function requestContent() {
    return {
        type: types.EP_REQUEST,
    };
}

function receiveModel(json){
    return {
        type: types.EP_RECEIVE_MODEL,
        model: json,
    };
}

function receiveObjects(json) {
    return {
        type: types.EP_RECEIVE_OBJECTS,
        items: json,
    };
}

function receiveObject(json) {
    return {
        type: types.EP_RECEIVE_OBJECT,
        item: json,
    };
}

function removeObject(id){
    return {
        type: types.EP_DELETE_OBJECT,
        id,
    };
}

function setEdititableObject(object){
    return {
        type: types.EP_CREATE_EDIT_OBJECT,
        object,
    };
}

function resetEditObject(field){
    return {
        type: types.EP_RESET_EDIT_OBJECT,
        field,
    };
}

function removeEditObjectIds(field, ids){
    return {
        type: types.EP_REMOVE_EDIT_OBJECT_IDS,
        field,
        ids,
    };
}

function patchItems(patch){
    return {
        type: types.EP_PATCH_OBJECTS,
        patch,
    };
}

function receiveEditErrors(errors){
    return {
        type: types.EP_RECEIVE_EDIT_ERRORS,
        errors,
    };
}

function releaseContent(){
    return {
        type: types.EP_RELEASE,
    };
}

export function fetchModelIfNeeded(){
    return (dispatch, getState) => {
        let state = getState();
        if (state.endpoint.isFetching) return;
        dispatch(requestContent());
        return fetch(
                h.getEndpointApiURL(state, false, true),
                h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveModel(json)))
            .catch((ex) => console.error('Endpoint parsing failed', ex));
    };
}

export function fetchObjectsIfNeeded(ids=null) {
    return (dispatch, getState) => {
        let state = getState();
        if (state.endpoint.isFetching) return;
        dispatch(requestContent());
        return fetch(h.getEndpointApiURL(state, false, false, ids), h.fetchGet)
            .then((response) => response.json())
            .then((json) => {
                if (ids === null){
                    dispatch(receiveObjects(json));
                } else {
                    _.map(json, (item) => {
                        dispatch(receiveObject(item));
                    });
                }
            })
            .catch((ex) => console.error('Endpoint parsing failed', ex));
    };
}

export function patchBulkList(patchObject){
    return (dispatch, getState) => {
        let state = getState(),
            { ids, field, stale } = patchObject,
            patch = {[field]: patchObject[field]},
            opts = h.fetchBulk(state.config.csrf, patch, 'PATCH');
        return fetch(
            `${h.getEndpointApiURL(state)}&ids=${ids}`,
            opts)
            .then((response) => {
                patchObject = _.omit(patchObject, 'stale');
                dispatch(resetEditObject(stale));
                dispatch(setEdititableObject(patchObject));
                if (response.ok){
                    dispatch(patchItems(patchObject));
                } else {
                    response.json()
                    .then((json) => dispatch(receiveEditErrors(json)));
                }
            })
            .catch((ex) => console.error('Endpoint parsing failed', ex));
    };
}

export function patchDetailList(patchObject){
    return (dispatch, getState) => {
        let state = getState(),
            { ids, field, stale } = patchObject,
            patch = {[field]: patchObject[field]},
            opts = h.fetchBulk(state.config.csrf, patch, 'PATCH');
        return fetch(
            `${h.getEndpointApiURL(state)}&ids=${ids}`,
            opts)
            .then((response) => {
                patchObject = _.omit(patchObject, 'stale');
                dispatch(removeEditObjectIds(stale, ids));
                dispatch(setEdititableObject(patchObject));
                if (response.ok){
                    dispatch(fetchObjectsIfNeeded(ids));
                } else {
                    response.json()
                    .then((json) => dispatch(receiveEditErrors(json)));
                }
            })
            .catch((ex) => console.error('Endpoint parsing failed', ex));
    };
}

export function deleteObject(id){
    return (dispatch, getState) => {
        let state = getState(),
            opts = h.fetchDelete(state.config.csrf);
        return fetch(
                h.getEndpointApiURL(state),
                opts)
            .then(function(response){
                if (response.status === 204){
                    dispatch(removeObject(id));
                } else {
                    response.json()
                        .then((json) => dispatch(receiveEditErrors(json)));
                }
            })
            .catch((ex) => console.error('Endpoint parsing failed', ex));
    };
}

export function releaseEndpoint(){
    return (dispatch) => {
        dispatch(releaseContent());
    };
}

export function initializeBulkEditForm(ids=[], field='system'){
    return (dispatch, getState) => {
        let state = getState(),
            thisField, object;
        if (ids){
            thisField = _.findWhere(state.endpoint.items, {id: ids[0]})[field];
            object = {
                ids,
                [field]: thisField,
                field: [field],
            };
        } else {
            object = {
                ids: [],
                [field]: '',
                field: [field],
            };
        }
        dispatch(setEdititableObject(object));
    };
}
