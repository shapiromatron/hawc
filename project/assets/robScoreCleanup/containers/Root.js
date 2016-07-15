import React, { Component, PropTypes } from 'react';
import { Provider } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import { fetchStudies } from 'robScoreCleanup/actions/Items';
import { fetchMetricOptions } from 'robScoreCleanup/actions/Metrics';

import MetricSelect from 'robScoreCleanup/containers/MetricSelect';
import MetricForm from 'robTable/components/MetricForm';
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

    componentWillMount(){
        this.props.store.dispatch(loadConfig());
    }

    componentDidMount() {
        this.props.store.dispatch(fetchStudies());
        this.props.store.dispatch(fetchMetricOptions());
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
        let store = this.props.store,
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
            state = store.getState();
        console.log(state.metrics.items)
        return (
            <Provider store={store}>
                <div>
                    <MetricSelect />
                    <div>
                        <select multiple name="" id="">
                        {_.map(this.state.scores, (score) => {
                            return <option value={score.id}>{score.value}</option>;
                        })}
                        </select>
                    </div>
                    <div>
                        <button className='btn btn-primary' onClick={this.loadMetrics}>
                            Load Metrics
                        </button>
                        <button className='btn' onClick={this.clearMetrics}>
                            Clear Results
                        </button>
                    </div>
                    <MetricForm metric={metric} config={config}/>
                </div>
            </Provider>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object.isRequired,
};

export default Root;
