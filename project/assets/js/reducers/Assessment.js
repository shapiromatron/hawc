import * as types from 'constants/ActionTypes';
import _ from 'underscore';

let defaultState = {
    isFetching: false,
    itemsLoaded: false,
    active: null,
    items: [],
};

export default function (state=defaultState, action){
    let index, items;
    switch (action.type){

    case types.AS_REQUEST:
        return Object.assign({}, state, {
            isFetching: true,
        });

    case types.AS_RECEIVE_OBJECT:
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

    case types.AS_RELEASE:
        return Object.assign({}, state, {
            active: null,
        });

    case types.AS_SELECT:
        return Object.assign({}, state, {
            active: action.object,
        });


    default:
        return state;
    }
}
