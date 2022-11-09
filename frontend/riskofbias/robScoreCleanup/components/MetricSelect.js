import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import SelectInput from "shared/components/SelectInput";

@observer
class MetricSelect extends Component {
    render() {
        const {selectedMetric, changeSelectedMetric, metricChoices} = this.props.store;
        return (
            <SelectInput
                id="selectMetric"
                name="selectMetric"
                choices={metricChoices}
                multiple={false}
                handleSelect={e => changeSelectedMetric(parseInt(e))}
                value={selectedMetric}
                label="Select the metric to edit"
            />
        );
    }
}
MetricSelect.propTypes = {
    store: PropTypes.object.isRequired,
};

export default MetricSelect;
