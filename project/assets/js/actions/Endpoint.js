import _ from 'underscore';
import * as types from '../constants/ActionTypes';
import h from '../utils/helpers';


function requestContent() {
    return {
        type: types.EP_REQUEST,
    };
}

function receiveModel(json){
    return {
        type: types.EP_RECIEVE_MODEL,
        model: json,
    };
}

function receiveObjects(json) {
    return {
        type: types.EP_RECEIVE_OBJECTS,
        items: json,
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

function receiveEditErrors(errors){
    return {
        type: types.EP_RECEIVE_EDIT_ERRORS,
        errors,
    };
}

function resetEditObject(){
    return {
        type: types.EP_RESET_EDIT_OBJECT,
    };
}

function releaseContent(){
    return {
        type: types.EP_RELEASE,
    };
}

export function fetchModelIfNeeded(assessment_id){
    return (dispatch, getState) => {
        let state = getState();
        if (state.endpoint.isFetching) return;
        dispatch(requestContent());
        return fetch(
                h.getApiURL(state.apiUrl, `${state.config.endpoint}fields/`, assessment_id),
                // `${state.apiUrl}/${state.config.endpoint}fields/?assessment_id=${assessment_id}`,
                h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveModel(json)))
            .catch((ex) => console.error('Endpoint parsing failed', ex));
    };
}

export function fetchObjectsIfNeeded() {
    return (dispatch, getState) => {
        let state = getState();
        if (state.endpoint.isFetching) return;
        dispatch(requestContent());
        return fetch(
                h.getApiURL(state.apiUrl, state.config.endpoint, assessment_id),
                h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveObjects(json)))
            .catch((ex) => console.error('Endpoint parsing failed', ex));
    };
}

export function patchObjects(ids, patch, cb){
    cb = cb || h.noop;
    return (dispatch, getState) => {
        let state = getState(),
            opts = h.fetchPost(state.config.csrf, patch, 'PATCH');
        return fetch(
                `${h.getApiURL(state.apiUrl, state.config.endpoint, assessment_id)}&ids=${ids}`,
                opts)
            .then(function(response){
                if (response.status === 200){
                    response.json()
                        .then((json) => dispatch(fetchObjectIfNeeded(json.id)))
                        .then(cb())
                        .then(() => dispatch(resetEditObject()));
                } else {
                    response.json()
                        .then((json) => dispatch(receiveEditErrors(json)));
                }
            })
            .catch((ex) => console.error('Endpoint parsing failed', ex));
    };
}

export function deleteObject(id, cb){
    cb = cb || h.noop;
    return (dispatch, getState) => {
        let state = getState(),
            opts = h.fetchDelete(state.config.csrf);
        return fetch(
                h.getApiURL(state.apiUrl, state.config.endpoint, assessment_id),
                opts)
            .then(function(response){
                if (response.status === 204){
                    dispatch(removeObject(id));
                    cb(null);
                } else {
                    response.json()
                        .then((json) => cb(json));
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

export function initializeEditForm(id=null){

    return (dispatch, getState) => {
        let state = getState(),
            object;
        if (id){
            object = _.findWhere(state.endpoint.items, {id});
            object = h.deepCopy(object);
        } else {
            object = {
                id: null,
                name: '',
                description: '',
                public: false,
                genome_assembly: 1,
                stranded: true,
                text: '',
            };
        }
        dispatch(setEdititableObject(object));
    };
}
