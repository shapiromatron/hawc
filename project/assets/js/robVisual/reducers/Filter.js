import * as types from '../constants/ActionTypes';


let defaultState = {
    robScoreThreshold: null,
    selectedEffects: [],
    endpoints: [],
    isFetchingEndpoints: false,
    endpointsLoaded: false,
    robScores: [],
    isFetchingRobScores: false,
    effects: [],
    isFetchingEffects: false,
    errors: [],
};

export default function (state=defaultState, action){
    switch (action.type){

    case types.REQUEST_EFFECTS:
        return Object.assign({}, state, {
            isFetchingEffects: true,
        });

    case types.RECEIVE_EFFECTS:
        return Object.assign({}, state, {
            isFetchingEffects: false,
            effects: action.effects,
        });

    case types.REQUEST_ENDPOINTS:
        return Object.assign({}, state, {
            isFetchingEndpoints: true,
        });

    case types.RECEIVE_ENDPOINTS:
        return Object.assign({}, state, {
            isFetchingEndpoints: false,
            endpointsLoaded: true,
            endpoints: action.endpoints,
        });

    case types.REQUEST_ROB_SCORES:
        return Object.assign({}, state, {
            isFetchingRobScores: true,
        });

    case types.RECEIVE_ROB_SCORES:
        return Object.assign({}, state, {
            isFetchingRobScores: false,
            robScores: action.robScores,
        });

    case types.SELECT_EFFECTS:
        return Object.assign({}, state, {
            selectedEffects: action.effects,
        });

    case types.SET_ROB_THRESHOLD:
        return Object.assign({}, state, {
            robScoreThreshold: action.threshold,
        });


    case types.RECEIVE_ERROR:
        return Object.assign({}, state, {
            errors: [ ...state.errors, action.error],
            isFetchingEffects: false,
            isFetchingRobScores: false,
            isFetchingEndpoints: false,
        });

    case types.CLEAR_ERRORS:
        return Object.assign({}, state, {
            errors: [],
        });

    default:
        return state;
    }
}
