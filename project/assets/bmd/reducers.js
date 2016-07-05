import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';
import * as types from 'bmd/constants';

const defaultState = {
    endpoint: null,
};

function bmd(state=defaultState, action){
    switch (action.type){

    case types.RECEIVE_ENDPOINT:
        return Object.assign({}, state, {
            endpoint: action.endpoint,
        });

    default:
        return state;
    }
}

const rootReducer = combineReducers({
    config,
    bmd,
});

export default rootReducer;
