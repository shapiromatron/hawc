import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import SelectInput from "shared/components/SelectInput";

@observer
class ValueDisplaySelect extends Component {
    render() {
        const {onChange, value} = this.props;
        return (
            <SelectInput
                label="Show value counts"
                choices={[
                    {id: 1, label: "Show counts & show colors"},
                    {id: 2, label: "Hide counts & show colors"},
                    {id: 3, label: "Hide counts & hide colors"},
                ]}
                handleSelect={value => onChange(parseInt(value))}
                value={value}
                helpText={"Show count information in heatmap and filters."}
                multiple={false}
            />
        );
    }
}
ValueDisplaySelect.propTypes = {
    onChange: PropTypes.func.isRequired,
    value: PropTypes.number.isRequired,
};

export default ValueDisplaySelect;
