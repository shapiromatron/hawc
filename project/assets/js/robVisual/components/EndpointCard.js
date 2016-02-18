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
            height = 200,
            width = 300,
            doses = this.groupByDoseUnit();
        return (
            <div className='span3'>
                <h4><a href={endpoint.url}>{endpoint.name}</a></h4>
                {_.map(doses, (dose) => {
                    return (
                        <DoseResponseChart className="doseResponseChart"
                            endpoint={endpoint}
                            doses={dose}
                            width={width}
                            height={height}
                        />
                    );
                })}
                <p>Extra content text here...</p>
                <button type='button' className='btn btn-default'>Show detail modal</button>
            </div>
        );
    }
}
