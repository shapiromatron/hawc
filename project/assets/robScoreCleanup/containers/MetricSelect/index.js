import React, { Component } from 'react';
import { connect } from 'react-redux';

import DisplayComponent from 'robScoreCleanup/components/MetricSelect';

export class MetricSelect extends Component {
  
    constructor(props) {
        super(props);
        this.selectMetric = this.selectMetric.bind(this);
    }

    componentWillMount() {
        
    }

    selectMetric(e){
        console.log(e)
    }

    render() {
        return (
            <DisplayComponent choices={this.props.choices} />
        );
    }
}

function mapStateToProps(state) {
    return {
        choices: state.metrics.items,
    };
}

export default connect(mapStateToProps)(MetricSelect);
