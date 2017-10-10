import { createStore, applyMiddleware, compose } from 'redux';
import thunk from 'redux-thunk';
import createLogger from 'redux-logger';

import rootReducer from '../reducers';


const logger = createLogger({
    level: 'info',
    collapsed: false,
    logger: console,
    predicate: (getState, action) => true,
});

const finalCreateStore = compose(
  applyMiddleware(thunk, logger),
  window.devToolsExtension ? window.devToolsExtension() : (f) => f
)(createStore);

export default function configureStore(initialState) {
    const store = finalCreateStore(rootReducer, initialState);

    if (module.hot) {
        // Enable Webpack hot module replacement for reducers
        module.hot.accept('../reducers', () => {
            const nextRootReducer = require('../reducers');
            store.replaceReducer(nextRootReducer);
        });
    }

    return store;
}
