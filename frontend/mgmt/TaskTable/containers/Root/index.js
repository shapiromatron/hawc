import React, {Component} from "react";
import PropTypes from "prop-types";
import {Provider} from "react-redux";

import {loadConfig} from "shared/actions/Config";
import List from "mgmt/TaskTable/containers/List";
import Loading from "shared/components/Loading";

class Root extends Component {
    componentWillMount() {
        this.props.store.dispatch(loadConfig());
    }

    render() {
        let store = this.props.store,
            state = store.getState(),
            App = Loading;
        if (state.config) {
            App = state.config.type ? List : Loading;
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
