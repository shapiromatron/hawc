import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';
import * as types from 'bmd/constants';

const defaultState = {
};

function bmd(state=defaultState, action){
    switch (action.type){

    default:
        return state;
    }
}

const rootReducer = combineReducers({
    config,
    bmd,
});

export default rootReducer;
