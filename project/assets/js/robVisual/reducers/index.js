import { combineReducers } from 'redux';

import filter from './Filter';
import config from './Config';

const rootReducer = combineReducers({
    filter,
    config,
});

export default rootReducer;
