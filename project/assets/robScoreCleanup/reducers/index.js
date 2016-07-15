import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';
import items from './Items';
import metrics from './Metrics';
import scores from './Scores';
import * as types from 'robScoreCleanup/constants';

const defaultState = {
    error: null,
};

function error(state=defaultState, action) {

    switch(action.type){

    case types.SET_ERROR:
        return Object.assign({}, state, {
            error: action.error,
        });

    case types.RESET_ERROR:
        return Object.assign({}, state, {
            error: null,
        });

    default:
        return state;
    }

}

const rootReducer = combineReducers({
    config,
    error,
    items,
    metrics,
    scores,
});

export default rootReducer;
