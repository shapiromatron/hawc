import * as types from 'constants/ActionTypes';
import _ from 'underscore';

let defaultState = {
    itemsLoaded: false,
    isFetching: false,
    model: null,
    items: [],
    editObject: {},
    editObjectErrors: {},
};

export default function (state=defaultState, action){
    let index, items, patch, ids;
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
            editObject: _.omit(state.editObject, action.field),
            editObjectErrors: {},
        });

    case types.EP_REMOVE_EDIT_OBJECT_IDS:
        patch = state.editObject[action.field];
        ids = patch.ids;
        action.ids.map((id) => {
            index = ids.indexOf(id);
            if (index >= 0){
                ids = [
                    ...ids.slice(0, index),
                    ...ids.slice(index + 1),
                ]
            }
        });
        return Object.assign({}, state, {
            editObject: {...state.editObject, [action.field]: {...patch, ids} },
        });

    case types.EP_CREATE_EDIT_OBJECT:
        let obj = action.object,
            field = obj.field,
            thisField = obj[field];
        if (state.editObject[thisField]){
            patch = { [thisField]: { ...obj, ids: state.editObject[thisField].ids.concat(obj.ids)}};
        } else {
            patch = { [thisField]: obj};
        }
        patch = state.editObject[thisField] ? { [thisField]: {...obj, ids: state.editObject[thisField].ids.concat(obj.ids)}} : {[thisField]: obj};
        return Object.assign({}, state, {
            editObject: { ...state.editObject, ...patch },
            editObjectErrors: {},
        });

    case types.EP_PATCH_OBJECTS:
        ids = action.patch.ids;
        patch = _.omit(action.patch, 'ids');
        items = state.items;
        ids.map((id) => {
            let index = state.items.indexOf(
                _.findWhere(state.items, {id})
            );
            if (index >= 0){
                items = [
                    ...items.slice(0, index),
                    Object.assign({}, items[index], {...patch, id}),
                    ...items.slice(index + 1),
                ];
            } else {
                items = [
                    ...items,
                    Object.assign({}, items[index], patch),
                ];
            }

        });
        return Object.assign({}, state, {
            items,
        });

    case types.EP_RECEIVE_EDIT_ERRORS:
        return Object.assign({}, state, {
            editObjectErrors: action.errors,
        });

    case types.EP_RELEASE:
        return Object.assign({}, defaultState);

    default:
        return state;
    }
}
