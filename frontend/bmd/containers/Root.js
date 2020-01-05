import React from 'react';
import PropTypes from 'prop-types';
import { Provider } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';

import Tabs from 'bmd/containers/Tabs';
import Modals from 'bmd/containers/Modals';

class Root extends React.Component {
    componentWillMount() {
        this.props.store.dispatch(loadConfig());
    }

    render() {
        let store = this.props.store;
        return (
            <Provider store={store}>
                <div>
                    <Tabs />
                    <Modals />
                </div>
            </Provider>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object.isRequired,
};

export default Root;
