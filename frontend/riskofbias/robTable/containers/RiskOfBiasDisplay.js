import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

import DisplayComponent from "../components/RiskOfBiasDisplay";
import ShowAll from "../components/ShowAll";

@inject("store")
@observer
class RiskOfBiasDisplay extends Component {
    render() {
        const {active, config, toggleShowAll, allRobShown} = this.props.store;
        return (
            <div className="riskofbias-container">
                <DisplayComponent active={active} config={config} />
                <ShowAll allShown={allRobShown} handleClick={toggleShowAll} />
            </div>
        );
    }
}

RiskOfBiasDisplay.propTypes = {
    store: PropTypes.object,
};

export default RiskOfBiasDisplay;
