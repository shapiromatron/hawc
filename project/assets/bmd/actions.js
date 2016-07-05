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

