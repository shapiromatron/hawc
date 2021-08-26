import React from "react";
import ReactDOM from "react-dom";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";

const Renderer = function(props) {
    return (
        <p>
            {props.dose} {props.units}
        </p>
    );
};

class EndpointCriticalDose {
    constructor(endpoint, span, type, show_units) {
        // custom field to observe dose changes and respond based on selected dose
        endpoint.addObserver(this);
        this.endpoint = endpoint;
        this.span = span;
        this.type = type;
        this.critical_effect_idx = endpoint.data[type];
        this.show_units = show_units;
        this.update();
    }

    update() {
        let ep = this.endpoint,
            doses = ep.doses.filter(v => v.name === ep.dose_units),
            dose = h.ff(doses[0].values[this.critical_effect_idx].dose),
            units = this.show_units ? ep.dose_units : "";

        ReactDOM.render(<Renderer dose={dose} units={units} />, this.span[0]);
    }
}

Renderer.propTypes = {
    dose: PropTypes.string,
    units: PropTypes.string,
};

export default EndpointCriticalDose;
