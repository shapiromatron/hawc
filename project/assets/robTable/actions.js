import fetch from 'isomorphic-fetch';

import * as types from 'robTable/constants';
import h from 'robTable/utils/helpers';


function requestStudy(){
    return {
        type: types.REQUEST,
    };
}

function receiveStudy(study){
    return {
        type: types.RECEIVE,
        study,
    };
}

function setMessage(message){
    return {
        type: types.SET_MESSAGE,
        message,
    };
}

function resetMessage(){
    return {
        type: types.RESET_MESSAGE,
    };
}

function setError(error){
    return {
        type: types.SET_ERROR,
        error,
    };
}

function resetError(){
    return {
        type: types.RESET_ERROR,
    };
}

function updateQualities(qualities){
    return {
        type: types.UPDATE_QUALITIES,
        qualities,
    };
}

function formatOutgoingRiskOfBias(state, riskofbias){
    let riskofbias_id = state.config.riskofbias.id,
        author,
        final,
        scores = _.flatten(_.map(state.study.riskofbiases, (domain) =>{
            return _.map(domain.values, (metric) => {
                return _.omit(
                    _.find(metric.values, (score) => {
                        if (score.riskofbias_id == riskofbias_id){
                            author = author || score.author;
                            final = final || score.final;
                        }
                        return score.riskofbias_id == riskofbias_id;
                    }),
                    ['riskofbias_id', 'author','final', 'domain_id', 'domain_name']
                );
            });
        }));
    return Object.assign({}, {
        author,
        final,
        scores,
        active: true,
        pk: parseInt(riskofbias_id),
        study: parseInt(state.config.study.id),
    }, riskofbias);
}

function formatIncomingStudy(study){
    let dirtyRoBs = _.filter(study.riskofbiases, (rob) => {return rob.active === true;});
    let domains = _.flatten(_.map(dirtyRoBs, (riskofbias) => {
        return _.map(riskofbias.scores, (score) => {
            return Object.assign({}, score, {
                riskofbias_id: riskofbias.id,
                author: riskofbias.author,
                final: riskofbias.final,
                domain_name: score.metric.domain.name,
                domain_id: score.metric.domain.id,
            });
        });
    }));

    let riskofbiases = d3.nest()
        .key((d) => { return d.metric.domain.name;})
        .key((d) => {return d.metric.metric;})
        .entries(domains);

    return Object.assign({}, study, {
        riskofbiases,
    });
}

export function fetchStudyIfNeeded(){
    return (dispatch, getState) => {
        let state = getState();
        if (state.isFetching || state.itemsLoaded) return;
        dispatch(requestStudy());
        dispatch(resetMessage());
        dispatch(resetError());
        return fetch(
                h.getObjectURL(
                    state.config.host,
                    state.config.study.url,
                    state.config.study.id), h.fetchGet)
            .then((response) => response.json())
            .then((json)     => formatIncomingStudy(json))
            .then((json)     => dispatch(receiveStudy(json)))
            .catch((ex)      => dispatch(setError(ex)));
    };
}

export function submitRiskOfBiasScores(scores){
    return (dispatch, getState) => {
        let state = getState(),
            patch = formatOutgoingRiskOfBias(state, scores),
            opts = h.fetchPost(state.config.csrf, patch, 'PUT');

        dispatch(resetMessage());
        dispatch(resetError());
        return fetch(
            `${h.getObjectURL(state.config.host,
                state.config.riskofbias.url,
                state.config.riskofbias.id)}`, opts)
            .then((response) => response.json())
            .then((json)     => dispatch(updateQualities(json.scores)))
            .then(()         => window.location.href = state.config.cancelUrl)
            .catch((ex)      => dispatch(setError(ex)));
    };
}
export function selectActive({domain, metric}){
    return {
        type: types.SELECT_ACTIVE,
        domain,
        metric,
    };
}
