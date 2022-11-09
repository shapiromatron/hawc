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
            hasSelectedModel = selected && selected.model !== null,
            output = hasSelectedModel ? selected.model.output : null,
            modelName = output ? output.model_name : <i>no model selected</i>;

        if (!selected) {
            return <p>Modeling not conducted, or results not available with these dose-units.</p>;
        }

        return (
            <div>
                <p>
                    <b>Selected model:</b>&nbsp;{modelName}
                    &nbsp;(<a href={selected.session_url}>View details</a>)
                </p>
                {hasSelectedModel ? (
                    <ul>
                        <li>
                            <b>BMDL:</b>&nbsp;{h.ff(output.BMDL)}&nbsp;{units}
                        </li>
                        <li>
                            <b>BMD:</b>&nbsp;{h.ff(output.BMD)}&nbsp;{units}
                        </li>
                        <li>
                            <b>BMDU:</b>&nbsp;{h.ff(output.BMDU)}&nbsp;{units}
                        </li>
                    </ul>
                ) : null}
                {selected.notes ? (
                    <p>
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
