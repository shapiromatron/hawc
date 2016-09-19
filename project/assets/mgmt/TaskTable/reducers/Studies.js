import * as types from 'mgmt/TaskTable/constants';


const defaultState = {
    isFetching: false,
    isLoaded: false,
    list: [],
};

function studies(state=defaultState, action) {
    switch (action.type) {
    case types.REQUEST_STUDIES:
        return Object.assign({}, state, {
            isFetching: true,
            isLoaded: false,
        });

    case types.RECEIVE_STUDIES:
        return Object.assign({}, state, {
            isFetching: false,
            isLoaded: true,
            list: action.studies,
        });

    default:
        return state;
    }
}

export default studies;
