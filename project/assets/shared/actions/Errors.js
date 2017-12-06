import * as sharedTypes from 'shared/constants/ActionTypes';

export function setError(error) {
    return {
        type: sharedTypes.SET_ERROR,
        error,
    };
}

export function resetError() {
    return {
        type: sharedTypes.RESET_ERROR,
    };
}
