import EndpointCriticalDose from "./EndpointCriticalDose";
import React from "react";
import ReactDOM from "react-dom";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";

const WrongUnitsRender = function(props) {
        return (
            <p>
                N/A
                <br />
                <span className="form-text text-muted">(BMD conducted using different units)</span>
            </p>
        );
    },
    ModelDetails = function(props) {
        const {output} = props.bmd;
        return [
            <p key={0}>
                <b>Selected model:</b> {output.model_name}
                &nbsp;(<a href={props.bmd.url}>View details</a>)
            </p>,
            <ul key={1}>
                <li>
                    <b>BMDL:</b> {h.ff(output.BMDL)} {props.units}
                </li>
                <li>
                    <b>BMD:</b> {h.ff(output.BMD)} {props.units}
                </li>
                <li>
                    <b>BMDU:</b> {h.ff(output.BMDU)} {props.units}
                </li>
            </ul>,
        ];
    },
    Renderer = function(props) {
        return (
            <div>
                {ModelDetails(props)}
                <p>{props.bmd_notes}</p>
            </div>
        );
    },
    NoneSelected = function(props) {
        return (
            <div>
                <p>
                    <i>BMD modeling conducted; no model selected</i> (
                    <a href={props.url}>View details</a>).
                </p>
                {props.bmd_notes ? (
                    <p>
                        <b>Modeling notes: </b>
                        {props.bmd_notes}
                    </p>
                ) : null}
            </div>
        );
    };

class BMDResult extends EndpointCriticalDose {
    update() {
        let bmd = this.endpoint.data.bmd,
            bmd_notes = this.endpoint.data.bmd_notes,
            url = this.endpoint.data.bmd_url;

        if (bmd === null) {
            // eslint-disable-next-line react/no-render-return-value
            return ReactDOM.render(<NoneSelected bmd_notes={bmd_notes} url={url} />, this.span[0]);
        }

        let currentUnits = this.endpoint.doseUnits.activeUnit.id,
            units_string = this.endpoint.doseUnits.activeUnit.name,
            bmdUnits = this.endpoint.data.bmd.dose_units,
            RenderComponent = currentUnits == bmdUnits ? Renderer : WrongUnitsRender;

        ReactDOM.render(
            <RenderComponent bmd={bmd} bmd_notes={bmd_notes} units={units_string} />,
            this.span[0]
        );
    }
}

Renderer.propTypes = {
    bmd: PropTypes.shape({
        output: PropTypes.object,
        url: PropTypes.string,
    }),
    bmd_notes: PropTypes.string,
    units: PropTypes.string,
};
NoneSelected.propTypes = {
    bmd_notes: PropTypes.string,
    url: PropTypes.string,
};

export default BMDResult;
