import { createStore, applyMiddleware, compose } from 'redux';
import thunk from 'redux-thunk';

import addPromiseSupportToDispatch from './promisedDispatch';


const finalCreateStore = compose(
  applyMiddleware(thunk)
)(createStore);

export default function configureStore(reducer, initialState) {
    const store = finalCreateStore(reducer, initialState);
    store.dispatch = addPromiseSupportToDispatch(store);
    return store;
}
