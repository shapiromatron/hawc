import React, { Component } from 'react';
import { connect } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import { fetchMetricOptions } from 'robScoreCleanup/actions/Metrics';
import { fetchScoreOptions } from 'robScoreCleanup/actions/Scores';
import { fetchScores, clearScores } from 'robScoreCleanup/actions/Items';

import MetricForm from 'robScoreCleanup/containers/MetricForm';
import MetricSelect from 'robScoreCleanup/containers/MetricSelect';
import ScoreList from 'robScoreCleanup/containers/ScoreList';
import ScoreSelect from 'robScoreCleanup/containers/ScoreSelect';


class Root extends Component {

    constructor(props) {
        super(props);
        this.loadMetrics = this.loadMetrics.bind(this);
        this.clearMetrics = this.clearMetrics.bind(this);
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
        this.props.dispatch(clearScores());
    }

    loadMetrics(e) {
        e.preventDefault();
        this.props.dispatch(fetchScores());
    }

    render() {
        let { itemsLoaded, metricsLoaded, scoresLoaded, error } = this.props,
            { config } = this.state;
        return (
                <div>
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
                    {itemsLoaded ? <MetricForm config={config}/> : null}
                    {itemsLoaded ? <ScoreList config={config} /> : null}
                </div>
        );
    }
}
function mapStateToProps(state){
    const { metrics, items, scores, error } = state;
    return {
        metricsLoaded: metrics.isLoaded,
        scoresLoaded: scores.isLoaded,
        itemsLoaded: items.isLoaded,
        error,
    };
}

export default connect(mapStateToProps)(Root);
