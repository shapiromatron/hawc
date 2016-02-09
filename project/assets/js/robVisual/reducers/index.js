import { combineReducers } from 'redux';

import Filter from './Filter';
import config from './Config';

const rootReducer = combineReducers({
    Filter,
    config,
});

export default rootReducer;
