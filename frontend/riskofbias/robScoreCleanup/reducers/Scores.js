import * as types from "riskofbias/robScoreCleanup/constants";

const defaultState = {
    isFetching: false,
    isLoaded: false,
    selected: null,
    items: [],
};

function scores(state = defaultState, action) {
    switch (action.type) {
        case types.REQUEST_SCORE_OPTIONS:
            return Object.assign({}, state, {
                isFetching: true,
            });

        case types.RECEIVE_SCORE_OPTIONS:
            return Object.assign({}, state, {
                isFetching: false,
                isLoaded: true,
                items: action.items,
            });

        case types.SELECT_SCORES:
            return Object.assign({}, state, {
                selected: action.scores,
            });

        default:
            return state;
    }
}

export default scores;
