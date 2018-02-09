import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';
import * as types from 'robTable/constants';

const defaultState = {
    isFetching: false,
    itemsLoaded: false,
    error: null,
    name: '',
    final: [],
    riskofbiases: [],
    active: [],
    heroid: '',
};

function study(state=defaultState, action){
    switch (action.type){

    case types.REQUEST:
        return Object.assign({}, state, {
            isFetching: true,
        });

    case types.RECEIVE:
        return Object.assign({}, state, {
            name: action.study.short_citation,
            final: action.study.final,
            riskofbiases: action.study.riskofbiases,
            active: action.study.riskofbiases,
            isFetching: false,
            itemsLoaded: true,
            heroid: action.study.heroid,
        });

    case types.SET_ERROR:
        return Object.assign({}, state, {
            error: action.error,
        });

    case types.RESET_ERROR:
        return Object.assign({}, state, {
            error: null,
        });

    case types.UPDATE_FINAL_SCORES:
        return Object.assign({}, state, {
            final: action.score,
        });

    case types.SELECT_ACTIVE:
        if(_.isEmpty(action.domain) | action.domain === 'none'){
            return Object.assign({}, state, {
                active: [],
            });
        }
        if(action.domain === 'all'){
            return Object.assign({}, state, {
                active: state.riskofbiases,
            });
        }
        let domains = _.findWhere(state.riskofbiases, {key: action.domain});
        if(action.metric){
            let values = _.findWhere(domains.values, {key: action.metric});
            return Object.assign(
                {},
                state,
                { active: [Object.assign(
                    {},
                    domains,
                    {values: [values]})],
                }
            );
        }
        return Object.assign({}, state, {
            active: [domains],
        });

    default:
        return state;
    }
}

const rootReducer = combineReducers({
    config,
    study,
});

export default rootReducer;
