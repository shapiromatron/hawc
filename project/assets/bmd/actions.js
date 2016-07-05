import $ from '$';
import fetch from 'isomorphic-fetch';

import * as types from 'bmd/constants';

import Endpoint from 'Endpoint';


var showModal = function(name){
    return $('#' + name).modal('show');
};

var receiveEndpoint = function(endpoint){
    return {
        type: types.RECEIVE_ENDPOINT,
        endpoint,
    };
};

export function fetchEndpoint(id){
    return (dispatch, getState) => {
        const url = Endpoint.get_endpoint_url(id);
        return fetch(url)
            .then((response) => response.json())
            .then((json) => dispatch(receiveEndpoint(new Endpoint(json))))
            .catch((ex) => console.error('Endpoint parsing failed', ex));
    };
}

export function showOptionModal(){
    showModal(types.OPTION_MODAL_ID);
}

export function showBMRModal(){
    showModal(types.BMR_MODAL_ID);
}

export function showOutputModal(){
    showModal(types.OUTPUT_MODAL_ID);
}

export function execute(){
    return {
        type: 'execute',
    };
}

export function toggleVariance(){
    return {
        type: 'toggleVariance',
    };
}

export function createModel(modelName){
    return {
        type: 'createModel',
        modelName,
    };
}

export function updateModel(){
    return {
        type: 'updateModel',
    };
}

export function deleteModel(){
    return {
        type: 'deleteModel',
    };
}


export function createBmr(){
    return {
        type: 'createBmr',
    };
}

export function updateBmr(){
    return {
        type: 'updateBmr',
    };
}

export function deleteBmr(){
    return {
        type: 'deleteBmr',
    };
}

export function saveSelected(){
    return {
        type: 'saveSelected',
    };
}
