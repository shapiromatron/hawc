import $ from '$';

import * as types from 'bmd/constants';


var showModal = function(name){
    return $('#' + name).modal('show');
};

export function showOptionModal(){
    showModal(types.OPTION_MODAL_ID);
}

export function showBMRModal(){
    showModal(types.BMR_MODAL_ID);
}

export function showOutputModal(){
    showModal(types.OUTPUT_MODAL_ID);
}

