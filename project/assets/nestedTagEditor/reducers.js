import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';

import * as types from 'nestedTagEditor/constants';


const defaultState = {
    tagsLoaded: false,
    tags: [],
    parentOptions: [],
};

function tree(state=defaultState, action){
    switch (action.type){

    case types.RECEIVE_TAGLIST:
        return Object.assign({}, state, {
            tags: action.tags,
            parentOptions: action.parentOptions,
            tagsLoaded: true,
        });

    default:
        return state;
    }
}

const rootReducer = combineReducers({
    config,
    tree,
});

export default rootReducer;
