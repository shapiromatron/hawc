import React from 'react';
import { connect } from 'react-redux';

import DisplayComponent from 'robTable/components/MetricForm';


export class MetricForm extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            formMetric: {
                key: 'metric',
                values:[
                    {
                        id: 0,
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
            },
        };
    }

    shouldComponentUpdate(nextProps, nextState) {
        console.log('updateIds', this.props.items.updateIds)
        console.log('metric.id',this.state.formMetric.values[0].id)
        if (parseInt(this.props.items.updateIds[0]) !== this.state.formMetric.values[0].id) {
            return true;
        }
        return false;
    }

    componentWillUpdate(prevProps, prevState) {
        this.updateFormMetric();
    }

    updateFormMetric() {
        let { metrics, items } = this.props,
            { formMetric } = this.state,
            formMetricEdit = formMetric;
        if (metrics.isLoaded && formMetric.id !== metrics.selected.id){
            formMetricEdit = {
                ...formMetric,
                key: metrics.selected.metric,
                values: [{ ...formMetric.values[0], metric: {...metrics.selected}}],
            };
        }
        if (!_.isEmpty(items.updateIds)) {
            let selectedScore = _.findWhere(items.items, {id: parseInt(_.first(items.updateIds))})
            formMetricEdit = {
                ...formMetricEdit,
                values: [Object.assign(formMetricEdit.values[0], selectedScore)],
            };
        }
        this.setState({formMetric: {...formMetricEdit}});
    }

    render() {
        console.log(this.state.formMetric)
        let { config } = this.props;
        return (
            <div><DisplayComponent metric={this.state.formMetric} config={config}/></div>
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
