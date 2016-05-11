import fetch from 'isomorphic-fetch';

import * as types from 'robAllTable/constants';
import h from 'robAllTable/utils/helpers';


function requestStudy(){
    return {
        type: types.REQUEST,
    };
}

function receiveStudy(study){
    return {
        type: types.RECEIVE,
        study,
    };
}

export function fetchStudy(id){
    return (dispatch, getState) => {
        let state = getState();
        if (state.isFetching) return;
        dispatch(requestStudy());
        return fetch(
                h.getObjectURL(
                    state.config.host,
                    state.config.study.url,
                    id,
                    state.config.assessment_id), h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveStudy(json)))
            .catch((ex) => console.error('Study parsing failed', ex));
    };
}
