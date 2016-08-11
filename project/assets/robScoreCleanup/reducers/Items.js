import * as types from 'robScoreCleanup/constants';

const defaultState = {
    isFetching: false,
    isLoaded: false,
    items: [],
    updateIds: [],
    editMetric: {
        key: 'metric',
        values:[
            {
                id: 0,
                riskofbias_id: 0,
                score: 10,
                score_description: 'Probably high risk of bias',
                score_shade: '#FFCC00',
                score_symbol: '-',
                notes: 'This will change to reflect the first selected metric.',
                metric: {
                    id: 0,
                    metric: '',
                    description: '',
                },
                author: {
                    full_name: '',
                },
            },
        ],
    },
};

function items(state=defaultState, action) {
    let list, index;
    switch(action.type){

    case types.REQUEST_ITEMS:
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
        if (index >= 0){
            list = [
                ...state.updateIds.slice(0, index),
                ...state.updateIds.slice(index + 1),
            ];
        } else {
            list = [
                ...state.updateIds,
                action.id,
            ];
        }
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

        return Object.assign({}, state, { items, });

    default:
        return state;
    }
}

export default items;
