import fetch from 'isomorphic-fetch';

import * as types from 'textCleanup/constants/ActionTypes';
import h from 'textCleanup/utils/helpers';

function requestContent() {
    return {
        type: types.AS_REQUEST,
    };
}

function receiveObject(item) {
    return {
        type: types.AS_RECEIVE_OBJECT,
        item,
    };
}

export function fetchAssessment() {
    return (dispatch, getState) => {
        let state = getState();
        if (state.assessment.isFetching) return;
        dispatch(requestContent());
        return fetch(h.getAssessmentApiUrl(state.config), h.fetchGet)
            .then(response => response.json())
            .then(json => dispatch(receiveObject(json)))
            .catch(ex => console.error('Assessment parsing failed', ex));
    };
}
