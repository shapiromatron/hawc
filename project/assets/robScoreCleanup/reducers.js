import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';
import * as types from 'robScoreCleanup/constants';

const defaultState = {
    isFetching: false,
    itemsLoaded: false,
    error: null,
    metric: null,
    studies: [],
};

function assessment(state=defaultState, action) {

    switch(action.type){

    case types.REQUEST:
        return Object.assign({}, state, {
            isFetching: true,
        });

    case types.RECEIVE:
        return Object.assign({}, state, {
            isFetching: false,
            itemsLoaded: true,
            studies: action.studies,
        });

    case types.SET_ERROR:
        return Object.assign({}, state, {
            error: action.error,
        });

    case types.RESET_ERROR:
        return Object.assign({}, state, {
            error: null,
        });

    case types.SELECT_METRIC:
        return Object.assign({}, state, {
            metric: action.metric,
        });

    default:
        return state;
    }

}

const rootReducer = combineReducers({
    config,
    assessment,
});

export default rootReducer;
