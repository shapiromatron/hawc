import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';
import tasks from 'mgmt/TaskTable/reducers/Tasks';


const rootReducer = combineReducers({
    config,
    tasks,
});

export default rootReducer;
