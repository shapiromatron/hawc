import _ from 'lodash';

import * as types from 'textCleanup/constants/ActionTypes';

let defaultState = {
    itemsLoaded: false,
    isFetching: false,
    model: null,
    list: [],
    editObject: {},
    editObjectErrors: {},
};

export default function(state = defaultState, action) {
    let index, list, patch, ids, field;
    switch (action.type) {
        case types.ITEM_REQUEST:
            return Object.assign({}, state, {
                isFetching: true,
            });

        case types.ITEM_RECEIVE_OBJECTS:
            return Object.assign({}, state, {
                list: action.items,
                isFetching: false,
                itemsLoaded: true,
            });

        case types.ITEM_RECEIVE_OBJECT:
            index = state.list.indexOf(
                _.find(state.list, { id: action.item.id })
            );
            if (index >= 0) {
                list = [
                    ...state.list.slice(0, index),
                    action.item,
                    ...state.list.slice(index + 1),
                ];
            } else {
                list = [...state.list, action.item];
            }
            return Object.assign({}, state, {
                isFetching: false,
                itemsLoaded: true,
                list,
            });

        case types.ITEM_RECEIVE_MODEL:
            return Object.assign({}, state, {
                isFetching: false,
                model: action.model.text_cleanup_fields,
            });

        case types.ITEM_RESET_EDIT_OBJECT:
            return Object.assign({}, state, {
                editObject: _.omit(state.editObject, action.field),
                editObjectErrors: {},
            });

        case types.ITEM_REMOVE_EDIT_OBJECT_IDS:
            patch = state.editObject[action.field];
            ids = patch.ids;
            action.ids.map((id) => {
                index = ids.indexOf(id);
                if (index >= 0) {
                    ids = [...ids.slice(0, index), ...ids.slice(index + 1)];
                }
            });
            return Object.assign({}, state, {
                editObject: {
                    ...state.editObject,
                    [action.field]: { ...patch, ids },
                },
            });

        case types.ITEM_CREATE_EDIT_OBJECT:
            field = action.object[action.object.field];
            if (state.editObject[field]) {
                patch = {
                    [field]: {
                        ...action.object,
                        ids: state.editObject[field].ids.concat(
                            action.object.ids
                        ),
                    },
                };
            } else {
                patch = { [field]: action.object };
            }
            return Object.assign({}, state, {
                editObject: { ...state.editObject, ...patch },
                editObjectErrors: {},
            });

        case types.ITEM_PATCH_OBJECTS:
            ids = action.patch.ids;
            patch = _.omit(action.patch, 'ids');
            list = state.list;
            ids.map((id) => {
                let index = state.list.indexOf(_.find(state.list, { id }));
                if (index >= 0) {
                    list = [
                        ...list.slice(0, index),
                        Object.assign({}, list[index], { ...patch, id }),
                        ...list.slice(index + 1),
                    ];
                } else {
                    list = [...list, Object.assign({}, list[index], patch)];
                }
            });
            return Object.assign({}, state, {
                list,
            });

        case types.ITEM_RECEIVE_EDIT_ERRORS:
            return Object.assign({}, state, {
                editObjectErrors: action.errors,
            });

        default:
            return state;
    }
}
