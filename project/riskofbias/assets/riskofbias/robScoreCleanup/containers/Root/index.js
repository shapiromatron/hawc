import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Provider } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';

import EditForm from 'riskofbias/robScoreCleanup/containers/EditForm';


class Root extends Component {

    componentWillMount() {
        this.props.store.dispatch(loadConfig());
    }

    render() {
        return (
            <Provider store={this.props.store}>
                <EditForm />
            </Provider>
        );
    }
}
Root.propTypes = {
    store: PropTypes.object.isRequired,
};

export default Root;
