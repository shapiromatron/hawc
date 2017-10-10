import { combineReducers } from 'redux';

import filter from './Filter';
import config from 'shared/reducers/Config';


const rootReducer = combineReducers({
    filter,
    config,
});

export default rootReducer;
