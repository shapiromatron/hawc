import fetch from "isomorphic-fetch";
import * as d3 from "d3";
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

function resetError() {
    return {
        type: types.RESET_ERROR,
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

export function selectActive({domain, metric}) {
    return {
        type: types.SELECT_ACTIVE,
        domain,
        metric,
    };
}
