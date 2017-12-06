import { createStore, applyMiddleware, compose } from 'redux';
import thunk from 'redux-thunk';
import { createLogger } from 'redux-logger';

import addPromiseSupportToDispatch from './promisedDispatch';

let finalCreateStore;

if (process.env.NODE_ENV === 'production') {
    finalCreateStore = compose(applyMiddleware(thunk))(createStore);
} else {
    // development
    const logger = createLogger({
        level: 'info',
        collapsed: false,
        logger: console,
        predicate: (getState, action) => true,
    });

    finalCreateStore = compose(
        applyMiddleware(thunk, logger),
        window.devToolsExtension ? window.devToolsExtension() : f => f
    )(createStore);
}

export default function configureStore(reducer, initialState) {
    const store = finalCreateStore(reducer, initialState);
    store.dispatch = addPromiseSupportToDispatch(store);
    return store;
}
