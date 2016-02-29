import * as types from 'robVisual/constants/ActionTypes';


const defaultState = {};

export default function (state=defaultState, action) {
    switch (action.type) {
    case types.CF_LOAD:
        let data = JSON.parse(document.getElementById('config').textContent);
        data.apiUrl = window ? window.location.origin : 'http://127.0.0.1:8000';
        return data;
    default:
        return state;
    }
}
