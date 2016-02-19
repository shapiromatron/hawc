import React, { Component, PropTypes } from 'react';

import h from 'utils/helpers';

import BulkForm from './BulkForm';
import './BulkList.css';


export default class BulkList extends Component {

    constructor(props) {
        super(props);
        this.state = props.endpoint;
    }

    handleChange(e) {
        let obj = {};
        obj[e.target.name] = h.getValue(e.target);
        this.setState({editObject: obj});
    }

    handleSubmit() {
        ids = _.map(groupedEndpoints, (group) => {
            return _.pluck(group, 'id');
        });
    }


    // Groups endpoints by the field to be edited.
    groupEndpoints(endpoint, field){
        return _.sortBy(_.groupBy(endpoint.items, (endpoint) => {
            return endpoint[field];
        }), (endpoint) => {
            return endpoint[0][field];
        });
    }

    render() {
        let { endpoint, params } = this.props,
            field = params.field,
            groupedEndpoints = this.groupEndpoints(endpoint, field);
        return (
            <div className='container-fluid'>
                <div className='row'>
                    <span className='bulk-header span4'>{h.caseToWords(field)}</span>
                    <span className='bulk-header span5'>{h.caseToWords(field)} edit</span>
                    <span className='bulk-header span2'>Submit</span>
                </div>

                    {_.map(groupedEndpoints, (endpoints) => {
                        return <BulkForm
                            key={endpoints[0][field] || 'Empty'}
                            items={endpoints}
                            field={field}/>;
                    })}
            </div>
        );
    }
}

BulkList.propTypes = {
    endpoint: PropTypes.shape({
        items: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.number.isRequired,
                name: PropTypes.string.isRequired,
            }).isRequired
        ),
    }),
    params: PropTypes.shape({
        type: PropTypes.string,
        field: PropTypes.string,
        id: PropTypes.string,
    }),
};
