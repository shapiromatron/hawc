import fetch from 'isomorphic-fetch';

import { setError, resetError } from 'riskofbias/robScoreCleanup/actions/Errors';
import * as types from 'riskofbias/robScoreCleanup/constants';
import h from 'shared/utils/helpers';
import { SCORE_TEXT_DESCRIPTION } from '../../constants';

function makeScoreOptionRequest() {
    return {
        type: types.REQUEST_SCORE_OPTIONS,
    };
}

function receiveScoreOptions(items) {
    return {
        type: types.RECEIVE_SCORE_OPTIONS,
        items,
    };
}

export function selectScores(scores) {
    return {
        type: types.SELECT_SCORES,
        scores,
    };
}

function formatScoreOptions(choices) {
    return choices.map((choice) => {
        return { id: choice, value: SCORE_TEXT_DESCRIPTION[choice] };
    });
}

export function fetchScoreOptions() {
    return (dispatch, getState) => {
        let state = getState();
        if (state.scores.isFetching || state.scores.isLoaded) return;
        dispatch(makeScoreOptionRequest());
        dispatch(resetError());
        let { host, scores, assessment_id } = state.config;
        const url = h.getUrlWithAssessment(h.getListUrl(host, scores.url), assessment_id);
        return fetch(url, h.fetchGet)
            .then((response) => response.json())
            .then((json) => formatScoreOptions(json))
            .then((json) => dispatch(receiveScoreOptions(json)))
            .catch((error) => dispatch(setError(error)));
    };
}
