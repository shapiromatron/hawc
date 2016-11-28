import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';

const rootReducer = combineReducers({
    config,
});

export default rootReducer;
