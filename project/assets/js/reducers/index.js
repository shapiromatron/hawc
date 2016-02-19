import { routerStateReducer as router } from 'redux-router';
import { combineReducers } from 'redux';

import config from './Config';
import assessment from './Assessment';
import endpoint from './Endpoint';

const rootReducer = combineReducers({
    router,
    config,
    assessment,
    endpoint,
});

export default rootReducer;
