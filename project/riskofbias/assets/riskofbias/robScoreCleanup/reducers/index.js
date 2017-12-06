import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';
import items from './Items';
import metrics from './Metrics';
import scores from './Scores';
import studyTypes from './StudyTypes';
import * as types from 'riskofbias/robScoreCleanup/constants';

const defaultState = {
    message: null,
};

function error(state = defaultState, action) {
    switch (action.type) {
        case types.SET_ERROR:
            return Object.assign({}, state, {
                message: action.error,
            });

        case types.RESET_ERROR:
            return Object.assign({}, state, {
                message: null,
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
    studyTypes,
});

export default rootReducer;
