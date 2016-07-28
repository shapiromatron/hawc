import fetch from 'isomorphic-fetch';

import { setError, resetError } from 'robScoreCleanup/actions/Errors';
import * as types from 'robScoreCleanup/constants';
import h from 'shared/utils/helpers';


function makeScoreOptionRequest(){
    return {
        type: types.REQUEST_SCORE_OPTIONS,
    };
}

function receiveScoreOptions(items){
    return {
        type: types.RECEIVE_SCORE_OPTIONS,
        items,
    };
}

export function selectScores(scores){
    return {
        type: types.SELECT_SCORES,
        scores,
    };
}

function formatScoreOptions(json){
    return _.map(json[0].RISK_OF_BIAS_SCORE_CHOICES, (choice) => {
        return {id: choice[0], value: choice[1]};
    });
}

export function fetchScoreOptions(){
    return (dispatch, getState) => {
        let state = getState();
        if (state.scores.isFetching || state.scores.isLoaded) return;
        dispatch(makeScoreOptionRequest());
        dispatch(resetError());
        let { host, scores, assessment_id } = state.config;
        const url = h.getUrlWithAssessment(
                        h.getListUrl(host, scores.url),
                        assessment_id);
        return fetch(url, h.fetchGet)
            .then((response) => response.json())
            .then((json) => formatScoreOptions(json))
            .then((json) => dispatch(receiveScoreOptions(json)))
            .catch((error) => dispatch(setError(error)));
    };
}

