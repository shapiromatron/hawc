import _ from 'lodash';

import * as types from 'riskofbias/robScoreCleanup/constants';
import { deepCopy } from 'shared/utils';

import { NR_KEY, SCORE_SHADES, SCORE_TEXT, SCORE_TEXT_DESCRIPTION } from '../../constants';

const defaultState = {
    isFetching: false,
    isLoaded: false,
    items: [],
    visibleItemIds: [],
    updateIds: [],
    editMetric: {
        key: 'metric',
        values: [
            {
                id: 0,
                riskofbias_id: 0,
                score: NR_KEY,
                score_description: SCORE_TEXT_DESCRIPTION[NR_KEY],
                score_shade: SCORE_SHADES[NR_KEY],
                score_symbol: SCORE_TEXT[NR_KEY],
                notes: 'This will change to reflect the first selected metric.',
                metric: {
                    id: 0,
                    name: '',
                    description: '',
                },
                author: {
                    full_name: '',
                },
            },
        ],
    },
};

function items(state = defaultState, action) {
    let list, list2, list3, intersection, index;
    switch (action.type) {
        case types.REQUEST_STUDY_SCORES:
            return Object.assign({}, state, {
                isFetching: true,
                isLoaded: false,
            });

        case types.RECEIVE_STUDY_SCORES:
            return Object.assign({}, state, {
                isFetching: false,
                isLoaded: true,
                items: action.items,
                updateIds: [],
            });

        case types.CLEAR_STUDY_SCORES:
            return Object.assign({}, state, {
                isLoaded: false,
                items: [],
                updateIds: [],
            });

        case types.CHECK_SCORE_FOR_UPDATE:
            index = state.updateIds.indexOf(action.id);
            if (index >= 0) {
                list = [...state.updateIds.slice(0, index), ...state.updateIds.slice(index + 1)];
            } else {
                list = [...state.updateIds, action.id];
            }
            return Object.assign({}, state, {
                updateIds: list,
            });

        case types.UPDATE_VISIBLE_ITEMS:
            // when the items, selected scores, or select study type change, we need to make sure
            // the following:
            // 1) `visibleItems` is the intersection of `items`, `selectedScores`, and 'selectedStudyTypes'
            // 2) `updateIds` is subset of `visibleItems`

            // visibleItems: selectedScores
            list =
                action.selectedScores === null || action.selectedScores.length === 0
                    ? _.map(state.items, 'id')
                    : state.items
                          .filter((d) => _.includes(action.selectedScores, d.score))
                          .map((d) => d.id);

            // visibleItems: selectedStudyTypes
            list2 =
                action.selectedStudyTypes === null || action.selectedStudyTypes.length === 0
                    ? _.map(state.items, 'id')
                    : state.items
                          .filter(
                              (d) =>
                                  _.intersection(action.selectedStudyTypes, d.study_types)
                                      .length !== 0
                          )
                          .map((d) => d.id);

            intersection = _.intersection(list, list2);

            // updateIds
            list3 = state.updateIds.filter((d) => _.includes(intersection, d));

            return Object.assign({}, state, {
                visibleItemIds: intersection,
                updateIds: list3,
            });

        case types.TOGGLE_CHECK_VISIBLE_SCORES:
            list =
                state.updateIds.length === state.visibleItemIds.length
                    ? []
                    : deepCopy(state.visibleItemIds);

            return Object.assign({}, state, {
                updateIds: list,
            });

        case types.UPDATE_EDIT_METRIC:
            return Object.assign({}, state, {
                editMetric: action.editMetric,
            });

        case types.PATCH_ITEMS:
            let ids = action.patch.ids,
                patch = _.omit(action.patch, 'ids'),
                items = state.items;

            _.map(ids, (id) => {
                let index = state.items.indexOf(_.find(state.items, { id }));
                if (index >= 0) {
                    items = [
                        ...items.slice(0, index),
                        Object.assign({}, items[index], { ...patch, id }),
                        ...items.slice(index + 1),
                    ];
                } else {
                    items = [...items, Object.assign({}, items[index], patch)];
                }
            });

            return Object.assign({}, state, { items });

        default:
            return state;
    }
}

export default items;
