import fetch from 'isomorphic-fetch';
import h from 'mgmt/utils/helpers';

import * as types from './constants';

function makeTaskRequest() {
    return {
        type: types.REQUEST_TASKS,
    };
}

export function hydrateTasks() {
    return (dispatch, getState) => {
        let state = getState(),
            { list, rob_tasks } = state.config.tasks;
        dispatch({
            type: types.HYDRATE_TASKS,
            list,
            robTasks: rob_tasks,
        });
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
        dispatch(makeTaskRequest());
        let { host, tasks } = state.config;
        const url = h.getListUrl(host, tasks.url);
        return fetch(url, h.fetchGet)
            .then((response) => response.json())
            .then((json) => dispatch(receiveTasks(json)));
    };
}
