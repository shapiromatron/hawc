import { createStore, applyMiddleware, compose } from 'redux';
import { reduxReactRouter } from 'redux-router';
import createHistory from 'history/lib/createBrowserHistory';
import thunk from 'redux-thunk';
import createLogger from 'redux-logger';

import routes from 'textCleanup/routes';
import rootReducer from 'textCleanup/reducers';


const logger = createLogger({
    level: 'info',
    collapsed: false,
    logger: console,
    predicate: (getState, action) => true,
});

const finalCreateStore = compose(
  applyMiddleware(thunk, logger),
  reduxReactRouter({ routes, createHistory }),
  window.devToolsExtension ? window.devToolsExtension() : (f) => f
)(createStore);

export default function configureStore(initialState) {
    return finalCreateStore(rootReducer, initialState);
}
