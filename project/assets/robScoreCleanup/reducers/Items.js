import * as types from 'robScoreCleanup/constants';

const defaultState = {
    isFetching: false,
    isLoaded: false,
    items: [],
    updateIds: [],
};

function items(state=defaultState, action) {
    let list;
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
        });

    case types.CLEAR_STUDY_SCORES:
        return Object.assign({}, state, {
            isLoaded: false,
            items: [],
        });

    case types.SELECT_SCORE_FOR_UPDATE:
        let updateIds = _.contains(state.updateIds, action.id) ? state.updateIds : [...state.updateIds, parseInt(action.id)];
        return Object.assign({}, state, {
            updateIds,
        });
    
    default:
        return state;
    }
}

export default items;