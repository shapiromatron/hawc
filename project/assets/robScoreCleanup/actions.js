import fetch from 'isomorphic-fetch';

import * as types from 'robScoreCleanup/constants';
import h from 'shared/utils/helpers';


function requestStudies(){
    return {
        type: types.REQUEST,
    };
}

function receiveStudies(studies){
    return {
        type: types.RECEIVE,
        studies,
    };
}

function setError(error){
    return {
        type: types.SET_ERROR,
        error,
    };
}

function resetError(){
    return {
        type: types.RESET_ERROR,
    };
}

export function fetchStudies(){
    return (dispatch, getState) => {
        let state = getState();
        if (state.isFetching || state.itemsLoaded) return;
        dispatch(requestStudies());
        dispatch(resetError());
        let { host, studies_url, assessment_id } = state.config;
        const url = h.getUrlWithAssessment(
                        h.getListUrl(host, studies_url),
                        assessment_id);
        return fetch(url, h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveStudies(json)))
            .catch((error) => dispatch(setError(error)));
    };
}
