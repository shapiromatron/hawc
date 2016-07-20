import React, { Component } from 'react';
import { connect } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import { fetchMetricOptions } from 'robScoreCleanup/actions/Metrics';
import { fetchScoreOptions } from 'robScoreCleanup/actions/Scores';
import { fetchScores, clearScores } from 'robScoreCleanup/actions/Items';

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
            formMetric: {
                key: 'metric',
                values:[
                    {
                        riskofbias_id: 0,
                        score: 4,
                        score_description: 'Probably high risk of bias',
                        score_shade: '#FFCC00',
                        score_symbol: '-',
                        notes: 'This will change to reflect the first selected metric.',
                        metric: {
                            id: 0,
                            metric: 'metric',
                            description: 'description',
                        },
                        author: {
                            full_name: '',
                        },
                    },
                ],

            }
        }
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
        this.updateFormMetric();
    }

    updateFormMetric() {
        let { selected, isLoaded } = this.props.state.metrics,
            { formMetric } = this.state;
        if (isLoaded && formMetric.id !== selected.id){
            this.setState({
                formMetric: {
                    ...formMetric,
                    key: selected.metric,
                    values: [{ ...formMetric.values[0], metric: {...selected}}],
                }
            });
        }
    }

    render() {
        let config = {
                display: 'all',
                isForm: 'false',
                riskofbias: {
                    id: 0,
                },
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
                    {items.isLoaded ? <MetricForm metric={this.state.formMetric} config={config}/> : null}
                    {items.isLoaded ? <ScoreList config={config} /> : null}
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
