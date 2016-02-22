import React, { Component, PropTypes } from 'react';
import _ from 'underscore';

import DoseResponseChart from './DoseResponseChart';


class EndpointCard extends Component {
    groupByDoseUnit() {
        let doses = this.props.endpoint.animal_group.dosing_regime.doses;
        return _.chain(doses)
            .map((dose) => { return {unit: dose.dose_units.name, dose:dose.dose}; })
            .groupBy('unit')
            .toArray()
            .value();
    }

    render(){
        let { endpoint } = this.props,
            doses = this.groupByDoseUnit(),
            responses =  _.map(endpoint.groups, (group) => {
                return {response: group.response, significant: group.significant, unit: endpoint.response_units};
            }),
            height = 150,
            width = 300,
            radius = 80,
            padding = [20, 5, 50, 60],
            yTransform = [padding[3], 0],
            xTransform = [0, height - padding[2]],
            chartData = {height, width, padding, yTransform, xTransform, radius};
        return (
            <div className='span3'>
                <h4><a href={endpoint.url}>{endpoint.name}</a></h4>
                <DoseResponseChart className="doseResponseChart"
                    endpoint={endpoint}
                    doses={doses[0]}
                    responses={responses}
                    chartData={chartData}
                />
                <p>Extra content text here...</p>
                <button type='button' className='btn btn-default'>Show detail modal</button>
            </div>
        );
    }
}

EndpointCard.propTypes = {
    endpoint: PropTypes.object.isRequired,
};

export default EndpointCard;
