import { routerStateReducer as router } from 'redux-router';
import { combineReducers } from 'redux';

import config from './Config';
import assessment from './Assessment';
import endpoint from './Endpoint';

const apiUrl = 'http://127.0.0.1:8000';

const rootReducer = combineReducers({
    apiUrl: apiUrl,
    router,
    config,
    assessment,
    endpoint,
});

export default rootReducer;
