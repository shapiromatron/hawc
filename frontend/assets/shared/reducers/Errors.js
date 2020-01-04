import * as sharedTypes from 'shared/constants/ActionTypes';

const defaultState = {
    message: null,
};

export default function error(state = defaultState, action) {
    switch (action.type) {
        case sharedTypes.SET_ERROR:
            return Object.assign({}, state, {
                message: action.error,
            });

        case sharedTypes.RESET_ERROR:
            return Object.assign({}, state, {
                message: null,
            });

        default:
            return state;
    }
}
