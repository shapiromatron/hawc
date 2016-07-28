import React from 'react';
import { connect } from 'react-redux';

import { updateEditMetricIfNeeded } from 'robScoreCleanup/actions/Items';

import DisplayComponent from 'robTable/components/MetricForm';


export class MetricForm extends React.Component {

    constructor(props) {
        super(props);
    }

    shouldComponentUpdate(nextProps, nextState) {
        if (_.isEqual(nextProps, this.props)){
            return false;
        }
        return true;
    }

    componentWillUpdate(prevProps, prevState) {
        this.props.dispatch(updateEditMetricIfNeeded());
    }

    render() {
        return (
            <DisplayComponent metric={this.props.items.editMetric} config={this.props.config}/>
        );
    }
}

function mapStateToProps(state) {
    const { items } = state;
    return {
        items,
    };
}

export default connect(mapStateToProps)(MetricForm);
