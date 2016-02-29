import React, { Component, PropTypes } from 'react';
import { Provider } from 'react-redux';
import { ReduxRouter } from 'redux-router';

import { loadConfig } from 'actions/Config';


class Root extends Component {
    componentWillMount() {
        this.props.store.dispatch(loadConfig());
    }

    render() {
        const { store } = this.props;
        return (
            <Provider store={store}>
                <ReduxRouter />
            </Provider>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object.isRequired,
};

export default Root;
