import fetch from 'isomorphic-fetch';

import { setError, resetError } from 'robScoreCleanup/actions/Errors';
import * as types from 'robScoreCleanup/constants';
import h from 'robScoreCleanup/utils/helpers';


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

export function clearItemScores() {
    return {
        type: types.CLEAR_STUDY_SCORES,
    };
}

export function checkScoreForUpdate(id) {
    return {
        type: types.CHECK_SCORE_FOR_UPDATE,
        id: parseInt(id),
    };
}

export function fetchItemScores(){
    return (dispatch, getState) => {
        let state = getState();
        if (state.items.isFetching) return;
        dispatch(clearItemScores());
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

function updateEditMetric(editMetric) {
    return {
        type: types.UPDATE_EDIT_METRIC,
        editMetric,
    };
}

function patchItems(patch){
    return {
        type: types.PATCH_ITEMS,
        patch,
    };
}

function addItemToMetric(item, current){
    let valueUpdate = Object.assign({}, current, item);
    return {
        key: item.metric.metric,
        values: [
            {
                ...valueUpdate,
            },
        ],
    };
}

function updateMetric(item, current){
    return {
        key: item.metric,
        values:[
            {
                ...current,
                metric: {
                    ...item,
                },
            },
        ],
    };
}

export function updateEditMetricIfNeeded() {
    return (dispatch, getState) => {
        let state = getState(),
            current = state.items.editMetric,
            update;
        if (!state.items.isLoaded) { 
        // update displayed metric and description to selected metric
            update = updateMetric(state.metrics.selected, current.values[0]);
            dispatch(updateEditMetric(update));
        } else if (_.isEmpty(state.items.updateIds)) {
        // if the selected metric changed, update displayed metric and description
            update = updateMetric(state.items.items[0].metric, current.values[0]);
            if (!_.isEqual(update, current)){
                dispatch(updateEditMetric(update));
            }
        } else {
        // update metricForm to reflect the first selected item
            let updateItem = _.findWhere(state.items.items, {id: state.items.updateIds[0]});
            update = addItemToMetric(updateItem, current.values[0]);
            dispatch(updateEditMetric(update));
        }
    };
}

export function submitItemEdits(metric) {
    return (dispatch, getState) => {
        dispatch(resetError());
        let state = getState(),
            { updateIds } = state.items,
            opts = h.fetchBulk(state.config.csrf, { ...metric});

        if (updateIds.length === 0) {
            dispatch(setError('A metric must be selected to update.'));
            return;
        }

        return fetch(h.buildPatchUrl(state.config, updateIds), opts)
        .then((response) => {
            if (response.ok){
                let patch = {ids: updateIds, ...metric};
                dispatch(patchItems(patch));
            } else {
                response.json()
                .then((json) => dispatch(setError(json)));
            }
        });
    };
}