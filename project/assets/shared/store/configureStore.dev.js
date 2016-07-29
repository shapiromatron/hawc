import { createStore, applyMiddleware, compose } from 'redux';
import thunk from 'redux-thunk';
import createLogger from 'redux-logger';


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

export default function configureStore(reducer, initialState) {
    const store = finalCreateStore(reducer, initialState);
    return store;
}
