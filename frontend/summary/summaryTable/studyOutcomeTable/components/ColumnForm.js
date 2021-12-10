import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import Alert from "shared/components/Alert";
import SelectInput from "shared/components/SelectInput";

@observer
class ColumnForm extends Component {
    render() {
        const {store} = this.props,
            typeChoices = store.rowTypeChoices,
            idChoices = store.rowIdChoices;

        if (idChoices.length === 0) {
            return (
                <Alert message="No data are available. Studies must be published and have at least one endpoint to be available for this summary table." />
            );
        }
        return (
            <div className="form-row">
                <div className="col-md-6">
                    <SelectInput
                        choices={typeChoices}
                        value={typeChoices[0].id}
                        handleSelect={value => console.log(value)}
                        label="Data type"
                    />
                </div>
                <div className="col-md-6">
                    <SelectInput
                        choices={idChoices}
                        value={idChoices[0].id}
                        handleSelect={value => console.log(value)}
                        label="Item"
                    />
                </div>
            </div>
        );
    }
}

ColumnForm.propTypes = {
    store: PropTypes.object.isRequired,
    instance: PropTypes.object,
};

export default ColumnForm;
