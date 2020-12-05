import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class MetricSelect extends Component {
    render() {
        const choices = _.map(this.props.store.metricOptions, choice => {
                return {id: choice.id, label: choice.name};
            }),
            selected = this.props.store.selectedMetric;

        return (
            <SelectInput
                id="metric-select"
                name="metric-select"
                choices={choices}
                multiple={false}
                handleSelect={e => {
                    this.props.store.changeSelectedMetric(parseInt(e));
                }}
                value={selected}
                label="Select the metric to edit"
            />
        );
    }
}
MetricSelect.propTypes = {
    store: PropTypes.object,
};

export default MetricSelect;
