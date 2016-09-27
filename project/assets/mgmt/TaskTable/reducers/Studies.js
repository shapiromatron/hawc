import _ from 'underscore';
import * as types from 'mgmt/TaskTable/constants';
import h from 'mgmt/utils/helpers';


const defaultState = {
    isFetching: false,
    isLoaded: false,
    list: [],
    visibleList: [],
    sortOrder: 'ascending',
};

function studies(state=defaultState, action) {
    let list;
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
            visibleList: action.studies,
        });

    case types.FILTER_STUDY_ON_TYPE:
        if (action.types.length === 0) {
            return Object.assign({}, state, {
                visibleList: state.list,
            });
        }

        list = action.types.map((type) => {
            return state.list.filter((study) => {
                return study[type];
            });
        });
        list = _.flatten(list);
        return Object.assign({}, state, {
            visibleList: list,
        });

    case types.SORT_STUDIES:
        list = state.list;
        /* if sorting field changed, sort */
        if (action.opts.field !== state.sortField){
            switch (action.opts.field) {
            case 'short_citation':
                list = h.sortStrings(list, action.opts.field);
                break;
            case 'created':
                list = h.sortDates(list, action.opts.field);
                break;
            default:
                list;
            }
            /* if sorting field changed and sorting order is descending, reverse list */
            if (action.opts.order === 'descending') list = list.reverse();
        } else {
            /* if sorting field didn't change, but sorting order did, reverse list */
            if (action.opts.order !== state.sortOrder) list = list.reverse();
        }
        return Object.assign({}, state, {
            list,
            sortOrder: action.opts.order,
            sortField: action.opts.field,
        });

    default:
        return state;
    }
}

export default studies;
