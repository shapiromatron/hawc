import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import SelectInput from "shared/components/SelectInput";

@observer
class RowForm extends Component {
    render() {
        const {store} = this.props,
            typeChoices = store.rowTypeChoices,
            idChoices = store.rowIdChoices;

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

RowForm.propTypes = {
    store: PropTypes.object.isRequired,
    instance: PropTypes.object,
};

export default RowForm;
