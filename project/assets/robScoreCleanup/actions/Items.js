import fetch from 'isomorphic-fetch';

import * as types from 'robScoreCleanup/constants';
import h from 'shared/utils/helpers';


function makeScoreRequest(){
    return {
        type: types.REQUEST_STUDY_SCORES,
    };
}

function receiveScores(items){
    return {
        type: types.RECEIVE_STUDY_SCORES,
        items,
    };
}

export function clearScores() {
    return {
        type: types.CLEAR_STUDY_SCORES,
    };
}

export function selectScoreForUpdate(id) {
    return {
        type: types.SELECT_SCORE_FOR_UPDATE,
        id,
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

export function fetchScores(){
    return (dispatch, getState) => {
        let state = getState();
        if (state.items.isFetching) return;
        dispatch(makeScoreRequest());
        dispatch(resetError());
        let { host, items, assessment_id } = state.config;
        const url = h.getUrlWithAssessment(
                        h.getObjectUrl(host, items.url, state.metrics.selected.id),
                        assessment_id);
        return fetch(url, h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveScores(json.scores)))
            .catch((error) => dispatch(setError(error)));
    };
}
