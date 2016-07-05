import $ from '$';
import fetch from 'isomorphic-fetch';

import * as types from 'bmd/constants';

import Endpoint from 'Endpoint';


var showModal = function(name){
        return $('#' + name).modal('show');
    },
    receiveEndpoint = function(endpoint){
        return {
            type: types.RECEIVE_ENDPOINT,
            endpoint,
        };
    },
    receiveSession = function(settings){
        return {
            type: types.RECEIVE_SESSION,
            settings,
        };
    },
    fetchEndpoint = function(id){
        return (dispatch, getState) => {
            const url = Endpoint.get_endpoint_url(id);
            return fetch(url)
                .then((response) => response.json())
                .then((json) => dispatch(receiveEndpoint(new Endpoint(json))))
                .catch((ex) => console.error('Endpoint parsing failed', ex));
        };
    },
    fetchSessionSettings = function(session_url){
        return (dispatch, getState) => {
            return fetch(session_url)
                .then((response) => response.json())
                .then((json) => dispatch(receiveSession(json)))
                .catch((ex) => console.error('Endpoint parsing failed', ex));
        };
    },
    setModel = function(modelIndex){
        return {
            type: types.SELECT_MODEL,
            modelIndex,
        };
    },
    showOptionModal = function(modelIndex){
        return (dispatch, getState) => {
            // create a new noop Promise to chain events
            return new Promise((res, rej)=>{res();})
                .then(() => dispatch(setModel(modelIndex)))
                .then(() => showModal(types.OPTION_MODAL_ID));
        };
    },
    showBMRModal = function(){
        showModal(types.BMR_MODAL_ID);
    },
    showOutputModal = function(){
        showModal(types.OUTPUT_MODAL_ID);
    },
    execute = function(){
        return {
            type: 'execute',
        };
    },
    toggleVariance = function(){
        return {
            type: 'toggleVariance',
        };
    },
    createModel = function(modelName){
        return {
            type: types.CREATE_MODEL,
            modelName,
        };
    },
    updateModel = function(){
        return {
            type: types.DELETE_MODEL,
        };
    },
    deleteModel = function(){
        return {
            type: types.DELETE_MODEL,
        };
    },
    createBmr = function(){
        return {
            type: 'createBmr',
        };
    },
    updateBmr = function(){
        return {
            type: 'updateBmr',
        };
    },
    deleteBmr = function(){
        return {
            type: 'deleteBmr',
        };
    },
    saveSelected = function(){
        return {
            type: 'saveSelected',
        };
    };

export {fetchEndpoint};
export {fetchSessionSettings};
export {showOptionModal};
export {showBMRModal};
export {showOutputModal};
export {execute};
export {toggleVariance};
export {createModel};
export {updateModel};
export {deleteModel};
export {createBmr};
export {updateBmr};
export {deleteBmr};
export {saveSelected};
