import * as ActionTypes from './actions';
import { routerStateReducer as router } from 'redux-router';
import merge from 'lodash/object/merge';
import { combineReducers } from 'redux';

let defaultState = {
    itemsLoaded: false,
    isFetching: false,
    items: [],
    editItems: [],
    editItemsErrors: [],
}

function entities(state = { assessment: {}, endpoint_type: {}, endpoint_fields: {}, endpoints: {}}, action){
    if (action.response && action.response.entities){
        return merge({}, state, action.response.entities);
    }

    return state;
}

// Updates error message
function errorMessage(state = null, action){
    const { type, error } = action;

    if (type == ActionTypes.RESEt_ERROR_MESSAGE){
        return null;
    } else if (error){
        return action.error;
    }

    return state;
}

const rootReducer = combineReducers({
    entities,
    errorMessage,
    router,
});

export default rootReducer;
