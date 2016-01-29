import { combineReducers } from 'redux';

import filters from './filters';

const rootReducer = combineReducers({
    filters,
});

export default rootReducer;
