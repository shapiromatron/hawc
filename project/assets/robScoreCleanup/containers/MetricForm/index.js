import React from 'react';
import { connect } from 'react-redux';

import { updateEditMetricIfNeeded } from 'robScoreCleanup/actions/Items';

import DisplayComponent from 'robTable/components/MetricForm';


export class MetricForm extends React.Component {

    constructor(props) {
        super(props);
        
    }

    render() {
        return (
            <div><DisplayComponent metric={this.props.items.editMetric} config={this.props.config}/></div>
        );
    }
}

function mapStateToProps(state) {
    const { metrics, items } = state;
    return {
        metrics,
        items,
    };
}

export default connect(mapStateToProps)(MetricForm);
