import React, { Component } from 'react';
import _ from 'underscore';

import DoseResponseChart from './DoseResponseChart';

export default class EndpointCard extends Component {
    groupByDoseUnit() {
        let doses = this.props.endpoint.animal_group.dosing_regime.doses;
        return _.chain(doses)
            .map((dose) => { return {unit: dose.dose_units.name, dose:dose.dose}; })
            .groupBy('unit')
            .value();
    }

    render(){
        let { endpoint } = this.props,
            doses = this.groupByDoseUnit(),
            height = 150,
            width = 300,
            padding = [20, 5, 40, 60],
            yTransform = [padding[3], 0],
            xTransform = [0, height - padding[2]],
            chartData = {height, width, padding, yTransform, xTransform};
        return (
            <div className='span3'>
                <h4><a href={endpoint.url}>{endpoint.name}</a></h4>
                {_.map(doses, (dose, i) => {
                    return (
                        <DoseResponseChart key={i} className="doseResponseChart"
                            endpoint={endpoint}
                            doses={dose}
                            chartData={chartData}
                        />
                    );
                })}
                <p>Extra content text here...</p>
                <button type='button' className='btn btn-default'>Show detail modal</button>
            </div>
        );
    }
}
