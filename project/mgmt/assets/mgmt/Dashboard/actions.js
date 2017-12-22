import fetch from 'isomorphic-fetch';
import h from 'mgmt/utils/helpers';

import { setError, resetError } from 'shared/actions/Errors';
import * as types from './constants';

function makeTaskRequest() {
    return {
        type: types.REQUEST_TASKS,
    };
}

function receiveTasks(tasks) {
    return {
        type: types.RECEIVE_TASKS,
        tasks,
    };
}

export function fetchTasks() {
    return (dispatch, getState) => {
        let state = getState();
        if (state.tasks.isFetching) return;
        let { host, tasks, assessment_id } = state.config;
        const url = h.getUrlWithAssessment(h.getListUrl(host, tasks.url), assessment_id);
        return fetch(url, h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveTasks(json)))
            .catch((error) => dispatch(setError(error)));
    };
}
