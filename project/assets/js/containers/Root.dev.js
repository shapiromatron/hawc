import React, { Component, PropTypes } from 'react';
import { Provider } from 'react-redux';
import { ReduxRouter } from 'redux-router';
import DevTools from './DevTools';

import { loadConfig } from 'actions/Config';

export default class Root extends Component {
    componentWillMount() {
        this.props.store.dispatch(loadConfig());
    }

    render() {
        const { store } = this.props;
        return (
            <Provider store={store}>
                <div>
                    <ReduxRouter />
                    <DevTools />
                </div>
            </Provider>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object.isRequired,
};
