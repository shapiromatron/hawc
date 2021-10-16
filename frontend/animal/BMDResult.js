import _ from "lodash";

import EndpointCriticalDose from "./EndpointCriticalDose";
import React from "react";
import ReactDOM from "react-dom";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";

class BmdResultComponent extends React.Component {
    render() {
        const {endpoint} = this.props,
            dose_units_id = endpoint.doseUnits.activeUnit.id,
            units = endpoint.doseUnits.activeUnit.name,
            selected = _.find(endpoint.data.bmds, d => d.bmd && d.bmd.dose_units === dose_units_id),
            hasSelectedModel = selected && selected.bmd !== null,
            output = hasSelectedModel ? selected.bmd.output : null;

        if (!selected) {
            return (
                <p>
                    N/A
                    <br />
                    <span className="form-text text-muted">
                        (BMD conducted using different units)
                    </span>
                </p>
            );
        } else {
            return (
                <div>
                    {hasSelectedModel ? (
                        <>
                            <p>
                                <b>Selected model:</b>&nbsp;{output.model_name}
                                &nbsp;(<a href={selected.bmd.url}>View details</a>)
                            </p>
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
                        </>
                    ) : (
                        <p>
                            <i>BMD modeling conducted; no model selected</i> (
                            <a href={selected.url}>View details</a>).
                        </p>
                    )}
                    {selected.notes ? (
                        <p>
                            <b>Modeling notes:</b>&nbsp;{selected.notes}
                        </p>
                    ) : null}
                </div>
            );
        }
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
