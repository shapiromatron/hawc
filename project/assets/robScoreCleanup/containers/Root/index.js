import React, { Component, PropTypes } from 'react';
import { Provider } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';

import EditForm from 'robScoreCleanup/containers/EditForm';


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
