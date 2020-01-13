import * as types from "textCleanup/constants/ActionTypes";

let defaultState = {
    isFetching: false,
    itemsLoaded: false,
    active: {},
};

export default function(state = defaultState, action) {
    switch (action.type) {
        case types.AS_REQUEST:
            return Object.assign({}, state, {
                isFetching: true,
                active: {},
            });

        case types.AS_RECEIVE_OBJECT:
            return Object.assign({}, state, {
                isFetching: false,
                itemsLoaded: true,
                active: action.item,
            });

        default:
            return state;
    }
}
