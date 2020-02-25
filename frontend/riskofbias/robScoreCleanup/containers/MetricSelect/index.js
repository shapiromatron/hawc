import React, {Component} from "react";
import {connect} from "react-redux";
import _ from "lodash";

import {selectMetric} from "riskofbias/robScoreCleanup/actions/Metrics";

import SelectInput from "shared/components/SelectInput";

export class MetricSelect extends Component {
    constructor(props) {
        super(props);
        this.handleSelect = this.handleSelect.bind(this);
    }

    formatMetricChoices() {
        return _.map(this.props.choices, choice => {
            return {id: choice.id, value: choice.name};
        });
    }

    handleSelect(option = null) {
        let choice = _.find(this.props.choices, {id: parseInt(option)});
        this.props.dispatch(selectMetric(choice));
    }

    render() {
        if (!this.props.isLoaded) return null;
        let choices = this.formatMetricChoices();
        return (
            <div>
                <SelectInput
                    id="metric-select"
                    name="metric-select"
                    className="span12"
                    choices={choices}
                    multiple={false}
                    handleSelect={this.handleSelect}
                    value={this.props.selected.id}
                    label="Select the metric to edit"
                />
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        selected: state.metrics.selected,
        isLoaded: state.metrics.isLoaded,
        choices: state.metrics.items,
    };
}

export default connect(mapStateToProps)(MetricSelect);
