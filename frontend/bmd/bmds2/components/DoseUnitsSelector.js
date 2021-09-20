import React from "react";
import PropTypes from "prop-types";

import SelectInput from "shared/components/SelectInput";

class DoseUnitsSelector extends React.Component {
    componentDidMount() {
        this.syncEndpoint(this.props.doseUnits);
    }

    syncEndpoint(id) {
        this.props.endpoint.switch_dose_units(id);
    }

    renderDoseForm() {
        let units = this.props.endpoint._get_doses_units();
        if (!this.props.editMode || units.length === 1) {
            return null;
        }

        const choices = units.map(d => {
                return {id: d.id, label: d.name};
            }),
            handleChange = id => {
                const intId = parseInt(id);
                this.syncEndpoint(intId);
                this.props.handleUnitsChange(intId);
            };

        return (
            <div className="col-md-3">
                <SelectInput
                    choices={choices}
                    handleSelect={handleChange}
                    value={this.props.doseUnits}
                    label="Dose units"
                />
            </div>
        );
    }

    render() {
        return (
            <div className="row">
                <div className="col-md-3">
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
