import React, { Component } from 'react';
import _ from 'underscore';

import DoseAxis from './xAxis';
import ResponseAxis from './yAxis';
import LineChart from './LineChart';

export default class DoseResponseChart extends Component {
    componentWillMount() {
        let { endpoint, doses } = this.props,
            responses =  _.map(endpoint.groups, (group) => { return {dose_id: group.dose_group_id, response: group.response}; }),
            doseData = this.getDoseAxisData(endpoint.animal_group.dosing_regime.doses),
            responseData = this.getResponseAxisData(responses),
            chartData = {...doses, ...responseData};

        this.setState({doseData, responseData, chartData});
    }

    getDoseAxisData(dose_group) {
        let { chartData, doses } = this.props;
        console.log("doses", doses);
        return {
            ...chartData,
            transform: chartData.xTransform,
            label: `Dose of ${doses[0].unit}`,
            min: _.min(_.pluck(dose_group, 'dose')),
            max: _.max(_.pluck(dose_group, 'dose')),
        };
    }

    getResponseAxisData(responses){
        let { chartData } = this.props;
        return {
            ...chartData,
            transform: chartData.yTransform,
            label: 'Response',
            min: _.min(_.pluck(responses, 'response')),
            max: _.max(_.pluck(responses, 'response')),
        };
    }

    render() {
        let { chartData } = this.props;
        return (
            <svg width={chartData.width} height={chartData.height}>
            <DoseAxis {...this.state.doseData} />
            {/*<LineChart data={this.state.chartData} />*/}
            <ResponseAxis {...this.state.responseData} />
            </svg>
        );
    }
}
