import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';
import * as types from 'robAllTable/constants';

const defaultState = {
    isFetching: false,
    itemsLoaded: false,
    name: '',
    qualities: [],
    riskofbiases: [],
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
            isFetching: false,
            itemsLoaded: true,
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
