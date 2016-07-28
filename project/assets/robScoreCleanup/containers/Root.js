import React, { Component } from 'react';
import { connect } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import { setError, resetError } from 'robScoreCleanup/actions/Errors';
import { fetchMetricOptions } from 'robScoreCleanup/actions/Metrics';
import { fetchScoreOptions } from 'robScoreCleanup/actions/Scores';
import { fetchItemScores, clearItemScores, updateEditMetricIfNeeded } from 'robScoreCleanup/actions/Items';

import ScrollToErrorBox from 'shared/components/ScrollToErrorBox';
import MetricForm from 'robScoreCleanup/containers/MetricForm';
import MetricSelect from 'robScoreCleanup/containers/MetricSelect';
import ScoreList from 'robScoreCleanup/containers/ScoreList';
import ScoreSelect from 'robScoreCleanup/containers/ScoreSelect';


class Root extends Component {

    constructor(props) {
        super(props);
        this.loadMetrics = this.loadMetrics.bind(this);
        this.clearMetrics = this.clearMetrics.bind(this);
        this.submitForm = this.submitForm.bind(this);
        this.handleCancel = this.handleCancel.bind(this);
        this.state = {
            config: {
                display: 'all',
                isForm: 'false',
                riskofbias: {
                    id: 0,
                },
            },
        };
    }

    componentWillMount() {
        this.props.dispatch(loadConfig());
    }

    componentDidMount() {
        this.props.dispatch(fetchMetricOptions());
        this.props.dispatch(fetchScoreOptions());
    }

    clearMetrics(e) {
        e.preventDefault();
        this.props.dispatch(resetError());
        this.props.dispatch(clearItemScores());
    }

    loadMetrics(e) {
        e.preventDefault();
        this.props.dispatch(resetError());
        this.props.dispatch(fetchItemScores());
        this.props.dispatch(updateEditMetricIfNeeded());
    }

    handleCancel(e) {
        e.preventDefault();
        this.props.dispatch(resetError());
    }

    submitForm(e) {
        e.preventDefault();
    }

    render() {
        let { items, metricsLoaded, scoresLoaded, error } = this.props,
            { config } = this.state;
        return (
                <div>
                    {error ? <ScrollToErrorBox error={error} /> : null}
                    {metricsLoaded ? <MetricSelect /> : null}
                    {scoresLoaded ? <ScoreSelect /> : null}
                    <div>
                        <button className='btn btn-primary' onClick={this.loadMetrics}>
                            Load Metrics
                        </button>
                        <button className='btn' onClick={this.clearMetrics}>
                            Clear Results
                        </button>
                    </div>
                    <form onSubmit={this.submitForm}>
                        {items.isLoaded ?
                            <div>
                                <MetricForm config={config} />
                                <button className='btn btn-primary' type='submit'>Update {items.updateIds.length} Metrics</button>
                                <button className='btn' onClick={this.handleCancel}>Cancel</button>
                                <ScoreList config={config} />
                            </div>
                            : null}
                    </form>
                </div>
        );
    }
}
function mapStateToProps(state){
    const { metrics, items, scores, error } = state;
    return {
        metricsLoaded: metrics.isLoaded,
        scoresLoaded: scores.isLoaded,
        items,
        error: error.error,
    };
}

export default connect(mapStateToProps)(Root);
