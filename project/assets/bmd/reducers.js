import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';
import * as types from 'bmd/constants';

const defaultState = {
    endpoint: null,
    dataType: null,
    models: [],
    selectedModelIndex: null,
    selectedModel: null,
    bmrs: [],
    allModelOptions: [],
    allBmrOptions: [],
};

function bmd(state=defaultState, action){
    switch (action.type){

    case types.RECEIVE_ENDPOINT:
        return Object.assign({}, state, {
            endpoint: action.endpoint,
            dataType: action.endpoint.data.data_type,
        });

    case types.RECEIVE_SESSION:
        return Object.assign({}, state, {
            models: action.settings.models,
            bmrs: action.settings.bmrs,
            allModelOptions: action.settings.allModelOptions,
            allBmrOptions: action.settings.allBmrOptions,
        });

    case types.CREATE_MODEL:
        return Object.assign({}, state, {
            models: [...state.models, state.allModelOptions[action.modelIndex]],
        });

    case types.SELECT_MODEL:
        return Object.assign({}, state, {
            selectedModelIndex: action.modelIndex,
            selectedModel: state.models[action.modelIndex],
        });

    case types.DELETE_MODEL:
        let tmp = state.models
            .slice(0, state.selectedModelIndex)
            .concat(state.models.slice(state.selectedModelIndex+1));
        return Object.assign({}, state, {
            models: tmp,
            selectedModelIndex: null,
            selectedModel: null,
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
