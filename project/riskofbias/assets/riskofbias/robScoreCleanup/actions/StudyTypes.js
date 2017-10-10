import fetch from 'isomorphic-fetch';

import { setError, resetError } from 'riskofbias/robScoreCleanup/actions/Errors';
import * as types from 'riskofbias/robScoreCleanup/constants';
import h from 'shared/utils/helpers';


function makeStudyTypeOptionRequest(){
    return {
        type: types.REQUEST_STUDY_TYPE_OPTIONS,
    };
}

function receiveStudyTypeOptions(items){
    return {
        type: types.RECEIVE_STUDY_TYPE_OPTIONS,
        items,
    };
}

export function selectStudyType(studyTypes){
    return {
        type: types.SELECT_STUDY_TYPE,
        studyTypes,
    };
}

export function fetchStudyTypeOptions(){
    return (dispatch, getState) => {
        let state = getState();
        if (state.studyTypes.isFetching || state.studyTypes.isLoaded) return;
        dispatch(makeStudyTypeOptionRequest());
        dispatch(resetError());
        let { host, studyTypes, assessment_id } = state.config;
        const url = h.getUrlWithAssessment(
                        h.getListUrl(host, studyTypes.url),
                        assessment_id);
        return fetch(url, h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveStudyTypeOptions(json)))
            .catch((error) => dispatch(setError(error)));
    };
}

