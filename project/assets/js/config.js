import * as types from '../constants/ActionTypes';


const defaultState = {};

export default function (state=defaultState, action) {
    switch (action.type) {
    case types.CF_LOAD:
        let data = JSON.parse(document.getElementById('config').textContent);
        data.csrf = data.csrf.match(/value='([\w]+)'/)[1];
        return data;
    default:
        return state;
    }
}
