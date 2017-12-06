import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';
import error from 'shared/reducers/Errors';
import studies from 'mgmt/TaskTable/reducers/Studies';
import tasks from 'mgmt/TaskTable/reducers/Tasks';

const rootReducer = combineReducers({
    config,
    error,
    studies,
    tasks,
});

export default rootReducer;
