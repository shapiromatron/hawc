import React, { Component } from 'react';
import { connect } from 'react-redux';
import _ from 'underscore';

import { selectMetric } from 'riskofbias/robScoreCleanup/actions/Metrics';

import ArraySelect from 'shared/components/ArraySelect';

export class MetricSelect extends Component {

    constructor(props) {
        super(props);
        this.handleSelect = this.handleSelect.bind(this);
    }

    setDefaultValue() {
        this.choices = this.formatMetricChoices();
        this.defaultValue = _.first(this.choices).id;
        this.handleSelect(this.defaultValue);
    }

    formatMetricChoices(){
        return _.map(this.props.choices, (choice) => {
            return {id: choice.id, value: choice.name};
        });
    }

    handleSelect(option=null){
        let choice = _.findWhere(this.props.choices, {id: parseInt(option)});
        this.props.dispatch(selectMetric(choice));
    }

    render() {
        if (!this.props.isLoaded) return null;
        this.setDefaultValue();
        return (
            <div>
                <label className='control-label'>Select the metric to edit:</label>
                <ArraySelect id='metric-select'
                    className='span12'
                    choices={this.choices}
                    handleSelect={this.handleSelect}
                    defVal={this.defaultValue}/>
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        isLoaded: state.metrics.isLoaded,
        choices: state.metrics.items,
    };
}

export default connect(mapStateToProps)(MetricSelect);
