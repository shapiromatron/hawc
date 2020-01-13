import * as sharedTypes from "shared/constants/ActionTypes";

const defaultState = {};

export default function(state = defaultState, action) {
    switch (action.type) {
        case sharedTypes.CF_LOAD:
            return JSON.parse(document.getElementById("config").textContent);
        default:
            return state;
    }
}
