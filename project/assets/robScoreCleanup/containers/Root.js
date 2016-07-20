import React, { Component } from 'react';
import { connect } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import { fetchStudies } from 'robScoreCleanup/actions/Items';
import { fetchMetricOptions } from 'robScoreCleanup/actions/Metrics';

import MetricForm from 'robTable/components/MetricForm';
import MetricSelect from 'robScoreCleanup/containers/MetricSelect';
import ScoreList from 'robScoreCleanup/containers/ScoreList';
import ScoreSelect from 'robScoreCleanup/containers/ScoreSelect';
import h from 'shared/utils/helpers';


class Root extends Component {

    constructor(props) {
        super(props);
        this.loadMetrics = this.loadMetrics.bind(this);
        this.clearMetrics = this.clearMetrics.bind(this);
        this.state = {
            scores: [
                {
                    id: 0,
                    value: 'Not applicable',
                },
                {
                    id: 1,
                    value: 'Definitely high risk of bias',
                },
                {
                    id: 2,
                    value: 'Probably high risk of bias',
                },
                {
                    id: 3,
                    value: 'Probably low risk of bias',
                },
                {
                    id: 4,
                    value: 'Definitely low risk of bias',
                },
                {
                    id: 10,
                    value: 'Not reported',
                },
            ],
        };
    }

    componentWillMount() {
        this.props.dispatch(loadConfig());
    }

    componentDidMount() {
        this.props.dispatch(fetchMetricOptions());
    }

    clearMetrics(e){
        e.preventDefault();
        console.log('clear metrics');
    }

    loadMetrics(e){
        e.preventDefault();
        console.log('load metrics');
    }

    render() {
            metric = {
                key: 'metric',
                values:[
                    {
                        riskofbias_id: 3,
                        score: 4,
                        notes: 'This will change to reflect the first selected metric.',
                        metric: {
                            metric: 'metric',
                            description: 'description',
                        },
                    },
                ]
            },
            config = {
                riskofbias: {
                    id: 3
                }
            },
            { items, metrics, scores, error } = this.props.state;

        return (
                <div>
                    {metrics.isLoaded ? <MetricSelect /> : null}
                    {scores.isLoaded ? <ScoreSelect /> : null}
                    <div>
                        <button className='btn btn-primary' onClick={this.loadMetrics}>
                            Load Metrics
                        </button>
                        <button className='btn' onClick={this.clearMetrics}>
                            Clear Results
                        </button>
                    </div>
                    {items.isLoaded ? <MetricForm /> : null}
                    {items.isLoaded ? <ScoreList /> : null}
                </div>
        );
    }
}
function mapStateToProps(state){
    return {
        state,
    };
};

export default connect(mapStateToProps)(Root);
