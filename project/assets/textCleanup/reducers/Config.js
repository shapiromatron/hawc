import * as types from 'textCleanup/constants/ActionTypes';


const defaultState = {};

export default function (state=defaultState, action) {
    switch (action.type) {
    case types.CF_LOAD:
        return JSON.parse(document.getElementById('config').textContent);
    default:
        return state;
    }
}
