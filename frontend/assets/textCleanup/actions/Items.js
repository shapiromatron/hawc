import 'babel-polyfill';
import _ from 'lodash';

import * as types from 'textCleanup/constants/ActionTypes';
import h from 'textCleanup/utils/helpers';

function requestContent() {
    return {
        type: types.ITEM_REQUEST,
    };
}

function receiveModel(json) {
    return {
        type: types.ITEM_RECEIVE_MODEL,
        model: json,
    };
}

function receiveObjects(json) {
    return {
        type: types.ITEM_RECEIVE_OBJECTS,
        items: json,
    };
}

function receiveObject(json) {
    return {
        type: types.ITEM_RECEIVE_OBJECT,
        item: json,
    };
}

function setEdititableObject(object) {
    return {
        type: types.ITEM_CREATE_EDIT_OBJECT,
        object,
    };
}

function resetEditObject(field) {
    return {
        type: types.ITEM_RESET_EDIT_OBJECT,
        field,
    };
}

function removeEditObjectIds(field, ids) {
    return {
        type: types.ITEM_REMOVE_EDIT_OBJECT_IDS,
        field,
        ids,
    };
}

function patchItems(patch) {
    return {
        type: types.ITEM_PATCH_OBJECTS,
        patch,
    };
}

function receiveEditErrors(errors) {
    return {
        type: types.ITEM_RECEIVE_EDIT_ERRORS,
        errors,
    };
}

export function fetchModel(routerParams) {
    return (dispatch, getState) => {
        let state = getState();
        if (state.items.isFetching) return;
        dispatch(requestContent());
        return fetch(
            h.getItemApiURL({
                state,
                filterFields: false,
                fetchModel: true,
                routerParams,
            }),
            h.fetchGet
        )
            .then((response) => response.json())
            .then((json) => dispatch(receiveModel(json)))
            .catch((ex) => console.error('Item parsing failed', ex));
    };
}

export function fetchObjects({ ids = null, routerParams = {} }) {
    return (dispatch, getState) => {
        let state = getState();
        if (state.items.isFetching) return;
        dispatch(requestContent());
        return fetch(
            h.getItemApiURL({
                state,
                filterFields: false,
                fetchModel: false,
                ids,
                routerParams,
            }),
            h.fetchGet
        )
            .then((response) => response.json())
            .then((json) => {
                if (ids === null) {
                    dispatch(receiveObjects(json));
                } else {
                    _.map(json, (item) => {
                        dispatch(receiveObject(item));
                    });
                }
            })
            .catch((ex) => console.error('Item parsing failed', ex));
    };
}

export function patchBulkList(patchObject, routerParams) {
    return (dispatch, getState) => {
        let state = getState(),
            { ids, field, stale } = patchObject,
            patch = { [field]: patchObject[field] },
            opts = h.fetchBulk(state.config.csrf, patch, 'PATCH');
        return fetch(h.getItemApiURL({ state, routerParams, ids }), opts)
            .then((response) => {
                patchObject = _.omit(patchObject, 'stale');
                dispatch(resetEditObject(stale));
                dispatch(setEdititableObject(patchObject));
                if (response.ok) {
                    dispatch(patchItems(patchObject));
                } else {
                    response.json().then((json) => dispatch(receiveEditErrors(json)));
                }
            })
            .catch((ex) => console.error('Item parsing failed', ex));
    };
}

export function patchDetailList(patchObject, routerParams) {
    return (dispatch, getState) => {
        let state = getState(),
            { ids, field, stale } = patchObject,
            patch = { [field]: patchObject[field] },
            opts = h.fetchBulk(state.config.csrf, patch, 'PATCH');
        return fetch(h.getItemApiURL({ state, routerParams, ids }), opts)
            .then((response) => {
                patchObject = _.omit(patchObject, 'stale');
                dispatch(removeEditObjectIds(stale, ids));
                dispatch(setEdititableObject(patchObject));
                if (response.ok) {
                    dispatch(fetchObjects({ ids, routerParams }));
                } else {
                    response.json().then((json) => dispatch(receiveEditErrors(json)));
                }
            })
            .catch((ex) => console.error('Item parsing failed', ex));
    };
}

export function initializeBulkEditForm(ids = [], field = 'system') {
    return (dispatch, getState) => {
        let state = getState(),
            thisField,
            object;
        if (ids) {
            thisField = _.find(state.items.list, { id: ids[0] })[field];
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
