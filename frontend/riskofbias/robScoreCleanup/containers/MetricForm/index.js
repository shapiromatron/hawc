import _ from 'lodash';
import React from 'react';
import { connect } from 'react-redux';

import { resetError } from 'riskofbias/robScoreCleanup/actions/Errors';
import { selectAll } from 'riskofbias/robScoreCleanup/actions/Items';
import {
    updateEditMetricIfNeeded,
    submitItemEdits,
} from 'riskofbias/robScoreCleanup/actions/Items';

import DisplayComponent from 'riskofbias/robTable/components/MetricForm';

export class MetricForm extends React.Component {
    constructor(props) {
        super(props);
        this.handleCancel = this.handleCancel.bind(this);
        this.handleSelectAll = this.handleSelectAll.bind(this);
        this.onSubmit = this.onSubmit.bind(this);
    }

    shouldComponentUpdate(nextProps, nextState) {
        if (!_.isEqual(nextProps, this.props) || !_.isEqual(nextState, this.state)) {
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

    handleSelectAll(e) {
        e.preventDefault();
        this.props.dispatch(selectAll());
    }

    onSubmit(e) {
        e.preventDefault();
        let { notes, score } = this.refs.metricForm.refs.form.state,
            metric = { notes, score: parseInt(score) };
        this.props.dispatch(submitItemEdits(metric));
    }

    render() {
        let { items, config, robResponseValues } = this.props;
        if (!items.isLoaded) return null;
        return (
            <form onSubmit={this.onSubmit}>
                <DisplayComponent
                    ref="metricForm"
                    metric={items.editMetric}
                    config={config}
                    updateNotesLeft={_.noop}
                    robResponseValues={robResponseValues}
                />
                <button type="submit" className="btn btn-primary space">
                    Update {items.updateIds.length} responses
                </button>
                <button type="button" className="btn btn-info space" onClick={this.handleSelectAll}>
                    Select/unselect all
                </button>
                <button type="button" className="btn" onClick={this.handleCancel}>
                    Cancel
                </button>
                <hr />
            </form>
        );
    }
}

function mapStateToProps(state) {
    const { items } = state;
    return {
        items,
        robResponseValues: _.map(state.scores.items, 'id'),
    };
}

export default connect(mapStateToProps)(MetricForm);
