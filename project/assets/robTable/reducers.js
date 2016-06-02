import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';
import * as types from 'robTable/constants';

const defaultState = {
    isFetching: false,
    itemsLoaded: false,
    error: null,
    message: null,
    name: '',
    qualities: [],
    riskofbiases: [],
    active: [],
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
            qualities: action.study.qualities,
            riskofbiases: action.study.riskofbiases,
            active: action.study.riskofbiases,
            isFetching: false,
            itemsLoaded: true,
        });

    case types.SET_MESSAGE:
        return Object.assign({}, state, {
            message: action.message,
        });

    case types.RESET_MESSAGE:
        return Object.assign({}, state, {
            message: null,
        });

    case types.SET_ERROR:
        return Object.assign({}, state, {
            error: action.error,
        });

    case types.RESET_ERROR:
        return Object.assign({}, state, {
            error: null,
        });

    case types.UPDATE_QUALITIES:
        return Object.assign({}, state, {
            qualities: action.qualities,
        });

    case types.SELECT_ACTIVE:
        if(_.isEmpty(action.domain)){
            return Object.assign({}, state, {
                active: domains,
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
