import _ from 'underscore';
import 'babel-polyfill';
import * as types from 'constants/ActionTypes';
import h from 'utils/helpers';


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

export function setType(endpoint_type){
    return {
        type: types.EP_SET_TYPE,
        endpoint_type,
    };
}

export function setField(field){
    return {
        type: types.EP_SET_FIELD,
        field,
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

function patchItems(ids, patch){
    return {
        type: types.EP_PATCH_OBJECTS,
        ids,
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
                h.getEndpointApiURL(state, true, true),
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

export function patchBulkList(objectList, cb){
    cb = cb || h.noop;
    return (dispatch, getState) => {
        let state = getState();
        _.map(objectList, (patchObject) => {
            let { ids, field } = patchObject,
                patch = {[field]: patchObject[field]},
                opts = h.fetchBulk(state.config.csrf, patch, 'PATCH');
            return fetch(
                `${h.getEndpointApiURL(state)}&ids=${ids}`,
                opts)
                .then((response) => {
                    dispatch(setEdititableObject(patchObject));
                    if (response.ok){
                        dispatch(patchItems(ids, patchObject));
                    } else {
                        response.json()
                        .then((json) => dispatch(receiveEditErrors(json)));
                    }
                })
                .catch((ex) => console.error('Endpoint parsing failed', ex));
        });
    };
}

export function patchDetailList(objectList, cb){
    cb = cb || h.noop;
    return (dispatch, getState) => {
        let state = getState();
        _.map(objectList, (patchObject) => {
            let { ids, field } = patchObject,
                patch = {[field]: patchObject[field]},
                opts = h.fetchBulk(state.config.csrf, patch, 'PATCH');
            return fetch(
                `${h.getEndpointApiURL(state)}&ids=${ids}`,
                opts)
                .then((response) => {
                    dispatch(setEdititableObject(patchObject));
                    if (response.ok){
                        dispatch(fetchObjectsIfNeeded(ids));
                    } else {
                        response.json()
                        .then((json) => dispatch(receiveEditErrors(json)));
                    }
                })
                .catch((ex) => console.error('Endpoint parsing failed', ex));
        });
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
  console.log(ids);
    return (dispatch, getState) => {
        let state = getState(),
            object;
        if (ids){
            object = _.findWhere(state.endpoint.items, {id: ids[0]});
            object = Object.assign({}, _.omit(object, ['id', 'name']), {ids, field: [field]} );
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
