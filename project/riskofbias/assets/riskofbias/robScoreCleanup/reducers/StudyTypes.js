import * as types from 'riskofbias/robScoreCleanup/constants';

const defaultState = {
    isFetching: false,
    isLoaded: false,
    selected: null,
    items: [],
};

function studyTypes(state=defaultState, action) {

    switch(action.type){

    case types.REQUEST_STUDY_TYPE_OPTIONS:
        return Object.assign({}, state, {
            isFetching: true,
        });

    case types.RECEIVE_STUDY_TYPE_OPTIONS:
        return Object.assign({}, state, {
            isFetching: false,
            isLoaded: true,
            items: action.items,
        });

    case types.SELECT_STUDY_TYPE:
        return Object.assign({}, state, {
            selected: action.studyTypes,
        });

    default:
        return state;
    }
}

export default studyTypes;