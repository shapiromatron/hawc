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

function formatRiskofBiases(study){
    let dirtyRoBs = _.filter(study.riskofbiases, (rob) => {return rob.active === true;});
    let domains = _.flatten(_.map(dirtyRoBs, (riskofbias) => {
        return _.map(riskofbias.scores, (score) => {
            return Object.assign({}, score, {
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

export function fetchStudyIfNeeded(id){
    return (dispatch, getState) => {
        let state = getState();
        if (state.isFetching || state.itemsLoaded) return;
        dispatch(requestStudy());
        return fetch(
                h.getObjectURL(
                    state.config.host,
                    state.config.study.url,
                    id,
                    state.config.assessment_id), h.fetchGet)
            .then((response) => response.json())
            .then((json) => formatRiskofBiases(json))
            .then((json) => dispatch(receiveStudy(json)))
            .catch((ex) => console.error('Study parsing failed', ex));
    };
}

export function selectActive({domain, metric}){
    return {
        type: types.SELECT_ACTIVE,
        domain,
        metric,
    };
}
