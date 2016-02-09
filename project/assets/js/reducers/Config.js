import * as types from 'constants/ActionTypes';


const defaultState = {};

export default function (state=defaultState, action) {
    switch (action.type) {
    case types.CF_LOAD:
        let data = JSON.parse(document.getElementById('config').textContent);
        data.csrf = data.csrf.match(/value='([\w]+)'/)[1];
        data.apiUrl = window ? window.location.origin : 'http://127.0.0.1:8000';
        return data;
    default:
        return state;
    }
}
