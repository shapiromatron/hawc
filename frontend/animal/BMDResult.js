import _ from "lodash";
import PropTypes from "prop-types";
import React from "react";
import {createRoot} from "react-dom/client";

import h from "shared/utils/helpers";

import EndpointCriticalDose from "./EndpointCriticalDose";

class BmdResultComponent extends React.Component {
    render() {
        const {endpoint} = this.props,
            dose_units_id = endpoint.doseUnits.activeUnit.id,
            units = endpoint.doseUnits.activeUnit.name,
            selected = _.find(endpoint.data.bmds, d => d.dose_units_id === dose_units_id),
            hasSelected = selected !== undefined,
            hasSelectedModel = hasSelected && selected.model,
            modelName = hasSelectedModel ? selected.model.name : <i>None selected</i>;

        if (!selected) {
            return (
                <span>Modeling not conducted, or results not available with these dose-units.</span>
            );
        }
        return (
            <ul className="list-unstyled mb-0">
                <li>
                    <b>Model:</b>&nbsp;{modelName}&nbsp;(
                    <a href={selected.session_url}>View</a>)
                </li>
                {selected.bmr ? (
                    <li>
                        <b>BMR:</b>&nbsp;{selected.bmr}
                    </li>
                ) : null}
                {selected.model ? (
                    <>
                        <li>
                            <b>BMDL:</b>&nbsp;{h.ff(selected.bmdl)}&nbsp;{units}
                        </li>
                        <li>
                            <b>BMD:</b>&nbsp;{h.ff(selected.bmd)}&nbsp;{units}
                        </li>
                        <li>
                            <b>BMDU:</b>&nbsp;{h.ff(selected.bmdu)}&nbsp;{units}
                        </li>
                    </>
                ) : null}
            </ul>
        );
    }
}
BmdResultComponent.propTypes = {
    endpoint: PropTypes.object.isRequired,
};

class BMDResult extends EndpointCriticalDose {
    update() {
        const root = createRoot(this.span[0]);
        root.render(<BmdResultComponent endpoint={this.endpoint} />);
    }
}

export default BMDResult;
