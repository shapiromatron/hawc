import { combineReducers } from 'redux';

import config from 'shared/reducers/Config';
import assessment from './Assessment';
import items from './Items';

const rootReducer = combineReducers({
    config,
    assessment,
    items,
});

export default rootReducer;
