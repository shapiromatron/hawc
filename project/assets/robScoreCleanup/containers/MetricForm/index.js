import React from 'react';
import { connect } from 'react-redux';

import { resetError } from 'robScoreCleanup/actions/Errors';
import { updateEditMetricIfNeeded, submitItemEdits } from 'robScoreCleanup/actions/Items';

import DisplayComponent from 'robTable/components/MetricForm';


export class MetricForm extends React.Component {

    constructor(props) {
        super(props);
        this.handleCancel = this.handleCancel.bind(this);
        this.onSubmit = this.onSubmit.bind(this);
    }

    shouldComponentUpdate(nextProps, nextState) {
        if (!_.isEqual(nextProps, this.props) ||
            !_.isEqual(nextState, this.state)){
            return true;
        }
        return false;
    }

    componentWillUpdate(prevProps, prevState) {
        this.props.dispatch(updateEditMetricIfNeeded());
    }

    handleCancel(e) {
        e.preventDefault();
        this.props.dispatch(resetError());
    }

    onSubmit(e){
        e.preventDefault();
        let { notes, score } = this.refs.metricForm.refs.form.state,
            metric = { notes, score };
        this.props.dispatch(submitItemEdits(metric));
    }

    render() {
        let { items, config } = this.props;
        return (
            <form onSubmit={this.onSubmit}>
                <DisplayComponent ref='metricForm' metric={items.editMetric} config={config}/>
                <button className='btn btn-primary' type='submit'>Update {items.updateIds.length} Metrics</button>
                <button className='btn' onClick={this.handleCancel}>Cancel</button>
            </form>
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
