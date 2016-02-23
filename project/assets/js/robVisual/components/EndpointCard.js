import React, { Component, PropTypes } from 'react';
import _ from 'underscore';

import CardHeader from './CardHeader';
import DoseResponseChart from './Graph/DoseResponseChart';
import Content from './Content';
import Endpoint from 'Endpoint';
import './EndpointCard.css';


class EndpointCard extends Component {
    groupByDoseUnit() {
        let doses = this.props.endpoint.animal_group.dosing_regime.doses;
        return _.chain(doses)
            .map((dose) => { return {unit: dose.dose_units.name, dose:dose.dose}; })
            .groupBy('unit')
            .toArray()
            .value();
    }

    showModal(e){
        Endpoint.displayAsModal(e.target.id);
    }

    getChartData(){
        let height = 150,
            width = 300,
            radius = 130,
            padding = [20, 0, 50, 55],
            yTransform = [padding[3], 0],
            xTransform = [0, height - padding[2]];
        return {height, width, padding, yTransform, xTransform, radius};
    }

    render(){
        let { endpoint, study } = this.props,
            doses = this.groupByDoseUnit(),
            responses =  _.map(endpoint.groups, (group) => {
                return {response: group.response, significant: group.significant, unit: endpoint.response_units};
            }),
            chartData = this.getChartData();
        return (
            <div className='endpointCard'>
                <CardHeader endpoint={endpoint} study={study} showModal={this.showModal.bind(this)} />
                <DoseResponseChart className="doseResponseChart"
                    endpoint={endpoint}
                    doses={doses[0]}
                    responses={responses}
                    chartData={chartData}
                />
                <Content endpoint={endpoint} />
            </div>
        );
    }
}

EndpointCard.propTypes = {
    endpoint: PropTypes.object.isRequired,
};

export default EndpointCard;
