import React, { Component, PropTypes } from 'react';
import { Provider } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import List from 'mgmt/TaskTable/containers/List';
import Edit from 'mgmt/TaskTable/containers/Edit';
import Loading from 'shared/components/Loading';



class Root extends Component {

    componentWillMount() {
        this.props.store.dispatch(loadConfig());
    }

    render() {
        let store = this.props.store,
            state = store.getState(),
            App = Loading;
        if (state.config){
            switch (state.config.type) {
            case 'display':
                App = List;
                break;
            case 'edit':
                App = Edit;
                break;
            default:
                App = Loading;
            }
        }
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
