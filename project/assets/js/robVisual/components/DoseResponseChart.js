import React, { Component } from 'react';
import _ from 'underscore';

import DoseAxis from './DoseAxis';
import LineChart from './LineChart';
import ResponseAxis from './ResponseAxis';

export default class DoseResponseChart extends Component {
    componentWillMount() {
        let { endpoint, doses } = this.props,
            responses =  _.map(endpoint.groups, (group) => { return {dose_id: group.dose_group_id, response: group.response}; }),
            doseData = this.getDoseAxisData(endpoint.animal_group.dosing_regime.doses),
            responseData = this.getResponseData(responses),
            chartData = {...doses, ...responseData};

        this.setState({doseData, responseData, chartData});
    }

    getDoseAxisData(doses) {
        return {
            minDose: _.min(_.pluck(doses, 'dose')),
            maxDose: _.max(_.pluck(doses, 'dose')),
            height: this.props.height,
        };
    }

    getResponseData(responses){
        return {
            minResponse: _.min((response) => { return response.response; }),
            maxResponse: _.max((response) => { return response.response; }),
            width: this.props.width,
        };
    }

    render() {
        return (
            <svg>
            <DoseAxis {...this.state.doseData} />
            {/*<LineChart data={this.state.chartData} />*/}
            <ResponseAxis {...this.state.responseData} />
            </svg>
        );
    }
}
