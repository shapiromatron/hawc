import fetch from "isomorphic-fetch";
import d3 from "d3";
import _ from "lodash";

import * as types from "riskofbias/robTable/constants";
import h from "riskofbias/robTable/utils/helpers";

function requestStudy() {
    return {
        type: types.REQUEST,
    };
}

function receiveStudy(study) {
    return {
        type: types.RECEIVE,
        study,
    };
}

function setError(error) {
    return {
        type: types.SET_ERROR,
        error,
    };
}

function addOverride(object) {
    return {type: types.ADD_NEW_OVERRIDE, object};
}

function removeOverride(score_id) {
    return {type: types.REMOVE_DELETED_OVERRIDE, score_id};
}

function resetError() {
    return {
        type: types.RESET_ERROR,
    };
}

function updateFinalScores(scores) {
    return {
        type: types.UPDATE_FINAL_SCORES,
        scores,
    };
}

export function scoreStateChange(score) {
    return {
        type: types.UPDATE_SCORE_STATE,
        score,
    };
}

export function createScoreOverride(data) {
    // todo update state on create
    return (dispatch, getState) => {
        let state = getState(),
            url = `${state.config.riskofbias.scores_url}?assessment_id=${state.config.assessment_id}`,
            csrf = state.config.csrf;

        return fetch(url, h.fetchPost(csrf, data, "POST"))
            .then(response => response.json())
            .then(json => dispatch(addOverride(json)))
            .catch(ex => dispatch(setError(ex)));
    };
}

export function deleteScoreOverride(data) {
    return (dispatch, getState) => {
        // todo update state on delete
        // the ids are required because of the BulkIdFilter
        let state = getState(),
            url = `${state.config.riskofbias.scores_url}${data.score_id}/?assessment_id=${state.config.assessment_id}&ids=${data.score_id}`,
            csrf = state.config.csrf;

        return fetch(url, h.fetchDelete(csrf))
            .then(response => {
                if (response.status === 204) {
                    dispatch(removeOverride(data.score_id));
                }
            })
            .catch(ex => dispatch(setError(ex)));
    };
}

function formatIncomingStudy(study) {
    let dirtyRoBs = _.filter(study.riskofbiases, rob => {
            return rob.active === true;
        }),
        domains = _.flattenDeep(
            _.map(dirtyRoBs, riskofbias => {
                return _.map(riskofbias.scores, score => {
                    return Object.assign({}, score, {
                        riskofbias_id: riskofbias.id,
                        author: riskofbias.author,
                        final: riskofbias.final,
                        domain_name: score.metric.domain.name,
                        domain_id: score.metric.domain.id,
                    });
                });
            })
        ),
        riskofbiases = d3
            .nest()
            .key(d => {
                return d.metric.domain.name;
            })
            .key(d => {
                return d.metric.name;
            })
            .entries(domains),
        finalRoB = _.find(dirtyRoBs, {final: true});

    return Object.assign({}, study, {
        riskofbiases,
        final: _.has(finalRoB, "scores") ? finalRoB.scores : [],
    });
}

export function fetchFullStudyIfNeeded() {
    return (dispatch, getState) => {
        let state = getState();
        if (state.isFetching || state.itemsLoaded) return;
        dispatch(requestStudy());
        dispatch(resetError());
        return fetch(
            h.getObjectUrl(state.config.host, state.config.study.url, state.config.study.id),
            h.fetchGet
        )
            .then(response => response.json())
            .then(json => formatIncomingStudy(json))
            .then(json => dispatch(receiveStudy(json)))
            .catch(ex => dispatch(setError(ex)));
    };
}

export function submitRiskOfBiasScores() {
    return (dispatch, getState) => {
        let state = getState(),
            scores = _.values(state.study.current_score_state),
            payload = {
                id: state.config.riskofbias.id,
                scores,
            },
            opts = h.fetchPost(state.config.csrf, payload, "PATCH"),
            url = `${h.getObjectUrl(
                state.config.host,
                state.config.riskofbias.url,
                state.config.riskofbias.id
            )}`;

        dispatch(resetError());
        return fetch(url, opts)
            .then(response => response.json())
            .then(json => dispatch(updateFinalScores(json.scores)))
            .then(() => (window.location.href = state.config.cancelUrl))
            .catch(ex => dispatch(setError(ex)));
    };
}

export function selectActive({domain, metric}) {
    return {
        type: types.SELECT_ACTIVE,
        domain,
        metric,
    };
}
