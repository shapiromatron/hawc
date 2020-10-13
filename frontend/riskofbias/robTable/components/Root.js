import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

import Header from "./Header";
// import AggregateGraph from "../containers/AggregateGraph";
// import RiskOfBiasDisplay from "../containers/RiskOfBiasDisplay";

@inject("store")
@observer
class Root extends Component {
    render() {
        return (
            <div>
                <Header />
                {/* <AggregateGraph /> */}
                <hr />
                {/* <RiskOfBiasDisplay /> */}
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
