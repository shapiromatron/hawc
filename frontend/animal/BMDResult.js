import EndpointCriticalDose from "./EndpointCriticalDose";
import React from "react";
import ReactDOM from "react-dom";
import PropTypes from "prop-types";

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
        return [
            <p key={0}>
                <b>Selected model:</b> {props.bmd.output.model_name}
                &nbsp;(<a href={props.bmd.url}>View details</a>)
            </p>,
            <ul key={1}>
                <li>
                    <b>BMDL:</b> {props.bmd.output.BMDL.toHawcString()} {props.units}
                </li>
                <li>
                    <b>BMD:</b> {props.bmd.output.BMD.toHawcString()} {props.units}
                </li>
                <li>
                    <b>BMDU:</b> {props.bmd.output.BMDU.toHawcString()} {props.units}
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

        let currentUnits = this.endpoint.dose_units_id,
            bmdUnits = this.endpoint.data.bmd.dose_units,
            units_string = this.endpoint.dose_units;

        let RenderComponent = currentUnits == bmdUnits ? Renderer : WrongUnitsRender;

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
