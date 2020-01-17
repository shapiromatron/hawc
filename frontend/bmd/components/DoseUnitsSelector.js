import React from "react";
import PropTypes from "prop-types";

class DoseUnitsSelector extends React.Component {
    componentWillMount() {
        this.syncEndpoint(this.props.doseUnits);
    }

    handleUnitsChange(evt) {
        let id = parseInt(evt.target.value);
        this.syncEndpoint(id);
        this.props.handleUnitsChange(id);
    }

    syncEndpoint(id) {
        this.props.endpoint.switch_dose_units(id);
    }

    renderDoseForm() {
        let units = this.props.endpoint._get_doses_units();
        if (!this.props.editMode || units.length === 1) {
            return null;
        }
        return (
            <div className="span3">
                <label className="control-label">Dose units used in modeling:</label>
                <div className="controls">
                    <select
                        name="dose_units"
                        value={this.props.doseUnits}
                        onChange={this.handleUnitsChange.bind(this)}>
                        {units.map(d => {
                            return (
                                <option key={d.id} value={d.id}>
                                    {d.name}
                                </option>
                            );
                        })}
                    </select>
                </div>
            </div>
        );
    }

    render() {
        return (
            <div className="row-fluid">
                <div className="span3">
                    <p>{this.props.version}</p>
                </div>
                {this.renderDoseForm()}
            </div>
        );
    }
}

DoseUnitsSelector.propTypes = {
    version: PropTypes.string.isRequired,
    editMode: PropTypes.bool.isRequired,
    endpoint: PropTypes.object.isRequired,
    doseUnits: PropTypes.number.isRequired,
    handleUnitsChange: PropTypes.func.isRequired,
};

export default DoseUnitsSelector;
