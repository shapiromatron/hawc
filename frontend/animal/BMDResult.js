import _ from "lodash";
import PropTypes from "prop-types";
import React from "react";
import ReactDOM from "react-dom";
import h from "shared/utils/helpers";

import EndpointCriticalDose from "./EndpointCriticalDose";

class BmdResultComponent extends React.Component {
    render() {
        const {endpoint} = this.props,
            dose_units_id = endpoint.doseUnits.activeUnit.id,
            units = endpoint.doseUnits.activeUnit.name,
            selected = _.find(endpoint.data.bmds, d => d.dose_units_id === dose_units_id),
            modelName = selected ? selected.name : <i>no model selected</i>;

        if (!selected) {
            return (
                <span>Modeling not conducted, or results not available with these dose-units.</span>
            );
        }
        return (
            <div>
                <p>
                    <b>Selected model:</b>&nbsp;{modelName}
                    &nbsp;(<a href={selected.session_url}>View details</a>)
                </p>
                {selected.name ? (
                    <ul>
                        <li>
                            <b>BMDL:</b>&nbsp;{h.ff(selected.bmdl)}&nbsp;{units}
                        </li>
                        <li>
                            <b>BMD:</b>&nbsp;{h.ff(selected.bmd)}&nbsp;{units}
                        </li>
                        <li>
                            <b>BMDU:</b>&nbsp;{h.ff(selected.bmdu)}&nbsp;{units}
                        </li>
                    </ul>
                ) : null}
                {selected.notes ? (
                    <p className="mb-0">
                        <b>Modeling notes:</b>&nbsp;{selected.notes}
                    </p>
                ) : null}
            </div>
        );
    }
}
BmdResultComponent.propTypes = {
    endpoint: PropTypes.object.isRequired,
};

class BMDResult extends EndpointCriticalDose {
    update() {
        ReactDOM.render(<BmdResultComponent endpoint={this.endpoint} />, this.span[0]);
    }
}

export default BMDResult;
