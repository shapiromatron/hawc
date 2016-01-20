import * as types from '../constants/ActionTypes';
import _ from 'underscore';

let defaultState = {
    itemsLoaded: false,
    isFetching: false,
    items: [],
    editObject: null,
    editObjectErrors: null,
};

export default function (state=defaultState, action){
    let index, items;
    switch (action.type){

    case types.AS_REQUEST:
        return Object.assign({}, state, {
            isFetching: true,
        });

    case types.AS_RECIEVE_OBJECTS:
        return Object.assign({}, state, {
            items: action.items,
            isFetching: false,
            itemsLoaded: true,
        });

    case types.AS_RECIEVE_OBJECT:
        index = state.items.indexOf(
            _.findWhere(state.items, {id: action.item.id})
        );
        if (index >= 0){
            items = [
                ...state.items.slice(0, index),
                action.item,
                ...state.items.slice(index + 1),
            ];
        } else {
            items = [
                ...state.items,
                action.item,
            ]
        }
        return Object.assign({}, state, {
            isFetching: false,
            items,
        });

    case types.AS_DELETE_OBJECT:
        index = state.items.indexOf(
            _.findWhere(state.items, {id: action.id})
        );
        if (index >= 0){
            items = [
                ...state.items.slice(0, index),
                ...state.items.slice(index + 1),
            ];
        }

        return Object.assign({}, state, {
            isFetching: false,
            items,
        });

    case types.AS_RESET_EDIT_OBJECT:
        return Object.assign({}, state, {
            editObject: null,
            editObjectErrors: {},
        });

    case types.AS_CREATE_EDIT_OBJECT:
        return Object.assign({}, state, {
            editObject: action.object,
            editObjectErrors: {},
        });

    case types.AS_RECEIVE_EDIT_ERRORS:
        return Object.assign({}, state, {
            editObjectErrors: action.errors,
        });

    default:
        return state;
    }
}
