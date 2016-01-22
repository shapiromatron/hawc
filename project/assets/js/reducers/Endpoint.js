import * as types from '../constants/ActionTypes';
import _ from 'underscore';

let defaultState = {
    itemsLoaded: false,
    isFetching: false,
    model: null,
    type: null,
    items: [],
    editObject: null,
    editObjectErrors: {},
};

export default function (state=defaultState, action){
    let index, items;
    switch (action.type){

    case types.EP_REQUEST:
        return Object.assign({}, state, {
            isFetching: true,
        });

    case types.EP_RECEIVE_OBJECTS:
        return Object.assign({}, state, {
            items: action.items,
            isFetching: false,
            itemsLoaded: true,
        });

    case types.EP_RECEIVE_OBJECT:
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
            ];
        }
        return Object.assign({}, state, {
            isFetching: false,
            itemsLoaded: true,
            items,
        });

    case types.EP_RECEIVE_MODEL:
        return Object.assign({}, state, {
            isFetching: false,
            model: action.model.text_cleanup_fields,
        });

    case types.EP_DELETE_OBJECT:
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

    case types.EP_RESET_EDIT_OBJECT:
        return Object.assign({}, state, {
            editObject: null,
            editObjectErrors: {},
        });

    case types.EP_CREATE_EDIT_OBJECT:
        return Object.assign({}, state, {
            editObject: action.object,
            editObjectErrors: {},
        });

    case types.EP_PATCH_OBJECTS:
        let indexes, items;
        items = state.items;
        indexes = action.ids.map((id) => {
            return state.items.indexOf(
                _.findWhere(state.items, {id})
            );
        });
        for (index of indexes) {
            if (index >= 0){
                items = [
                    ...items.slice(0, index),
                    Object.assign({}, items[index], state.editObject),
                    ...items.slice(index + 1),
                ];
            } else {
                items = [
                    ...items,
                    Object.assign({}, items[index], state.editObject),
                ];
            }
        }
        return Object.assign({}, state, {
            items,
        })

    case types.EP_RECEIVE_EDIT_ERRORS:
        return Object.assign({}, state, {
            editObjectErrors: action.errors,
        });

    default:
        return state;
    }
}
