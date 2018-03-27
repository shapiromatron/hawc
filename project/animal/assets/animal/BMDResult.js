import EndpointCriticalDose from './EndpointCriticalDose';
import React from 'react';
import ReactDOM from 'react-dom';

const WrongUnitsRender = function(props) {
        return (
            <p>
                N/A
                <br />
                <span className="help-block">(BMD conducted using different units)</span>
            </p>
        );
    },
    ModelDetails = function(props) {
        if (!props.bmd) {
            return (
                <p>
                    <b>BMD modeling conducted; no model selected.</b> (<a href={props.bmd.url}>
                        View details
                    </a>)
                </p>
            );
        }
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
    };

class BMDResult extends EndpointCriticalDose {
    update() {
        let bmd = this.endpoint.data.bmd,
            bmd_notes = this.endpoint.data.bmd_notes,
            currentUnits = this.endpoint.dose_units_id,
            bmdUnits = this.endpoint.data.bmd.dose_units,
            units_string = this.endpoint.dose_units;

        let RenderComponent = currentUnits == bmdUnits ? Renderer : WrongUnitsRender;

        ReactDOM.render(
            <RenderComponent bmd={bmd} bmd_notes={bmd_notes} units={units_string} />,
            this.span[0]
        );
    }
}

export default BMDResult;
