import React, {Component} from "react";
import PropTypes from "prop-types";
import {Provider} from "react-redux";

import {loadConfig} from "shared/actions/Config";
import Header from "./Header";
import RiskOfBias from "./RiskOfBias";

class Root extends Component {
    constructor(props) {
        super(props);
        this.props.store.dispatch(loadConfig());
    }

    render() {
        let store = this.props.store;
        return (
            <Provider store={store}>
                <div>
                    <Header />
                    <RiskOfBias />
                </div>
            </Provider>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object.isRequired,
};

export default Root;
