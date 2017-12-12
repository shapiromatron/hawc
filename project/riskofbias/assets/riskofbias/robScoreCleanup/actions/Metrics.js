import fetch from 'isomorphic-fetch';

import {
    setError,
    resetError,
} from 'riskofbias/robScoreCleanup/actions/Errors';
import * as types from 'riskofbias/robScoreCleanup/constants';
import h from 'shared/utils/helpers';

function makeMetricRequest() {
    return {
        type: types.REQUEST_METRIC_OPTIONS,
    };
}

function receiveMetrics(metrics) {
    return {
        type: types.RECEIVE_METRIC_OPTIONS,
        metrics,
    };
}

export function selectMetric(metric) {
    return {
        type: types.SELECT_METRIC,
        metric,
    };
}

export function fetchMetricOptions() {
    return (dispatch, getState) => {
        let state = getState();
        if (state.metrics.isFetching || state.metrics.isLoaded) return;
        dispatch(makeMetricRequest());
        dispatch(resetError());
        let { host, metrics, assessment_id } = state.config;
        const url = h.getUrlWithAssessment(
            h.getListUrl(host, metrics.url),
            assessment_id
        );
        return fetch(url, h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveMetrics(json)))
            .catch((error) => dispatch(setError(error)));
    };
}
