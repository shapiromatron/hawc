import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Provider } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import Assignments from 'mgmt/TaskAssignments/containers/Assignments';

class Root extends Component {
    componentWillMount() {
        this.props.store.dispatch(loadConfig());
    }

    render() {
        return (
            <Provider store={this.props.store}>
                <Assignments />
            </Provider>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object.isRequired,
};

export default Root;
