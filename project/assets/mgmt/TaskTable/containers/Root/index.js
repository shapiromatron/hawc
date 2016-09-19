import React, { Component, PropTypes } from 'react';
import { Provider } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import App from 'mgmt/TaskTable/containers/App';

class Root extends Component {

    componentWillMount() {
        this.props.store.dispatch(loadConfig());
    }

    render() {
        let store = this.props.store;
        return (
            <Provider store={store}>
                <App />
            </Provider>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object.isRequired,
};

export default Root;
