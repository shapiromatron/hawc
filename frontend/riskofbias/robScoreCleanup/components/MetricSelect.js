import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";

import SelectInput from "shared/components/SelectInput";

@observer
class MetricSelect extends Component {
    render() {
        const {isLoading, selectedMetric, changeSelectedMetric, metricChoices} = this.props.store;

        if (isLoading) {
            return null;
        }

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
