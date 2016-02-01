import React, { Component, PropTypes } from 'react';

import h from '../../utils/helpers';
import EndpointDetailEdit from './EndpointDetailEdit';
import FormFieldError from '../FormFieldError';

export default class EndpointBulkEdit extends Component {

    handleSubmit(){

    }

    handleChange(){
        
    }

    // renders a row for each group of endpoints
    renderBulkEdit(endpoints, field){
        let obj = endpoints[0],
            thisField = obj[field],
            errs = this.props.errors || {};
        return (
            <tr key={thisField} onSubmit={this.handleSubmit.bind(this)}>
                <td>{thisField || `${h.caseToWords(field)} Left Empty`}</td>
                <td className={h.getInputDivClass(thisField, errs)}>
                    <input name={thisField} className='form-control' type="text"
                        value={thisField}
                        onChange={this.handleChange.bind(this)}/>
                    <FormFieldError errors={errs.name} />
                </td>
                <td><button className='btn btn-primary'>Submit Bulk Edit</button></td>
            </tr>
        )
    }

    // Groups endpoints by the field to be edited.
    groupEndpoints(endpoint){
        let field = endpoint.field;
        return _.groupBy(endpoint.items, (endpoint) => {
            return endpoint[field];
        })
    }

    render() {
        let { endpoint } = this.props;
        let groupedEndpoints = this.groupEndpoints(endpoint);
        return (
            <table className='table table-condensed table-striped'>
                <thead>
                    <tr>
                        <th>{h.caseToWords(endpoint.field)}</th>
                        <th>{h.caseToWords(endpoint.field)} Edit</th>
                        <th>Submit Edit</th>
                    </tr>
                </thead>
                <tbody>
                    {_.map(groupedEndpoints, (endpoints) => {
                        return this.renderBulkEdit(endpoints, endpoint.field);
                    })}
                </tbody>
            </table>

        );
    }
}
