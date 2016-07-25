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
                score: 4,
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

    default:
        return state;
    }
}

export default items;