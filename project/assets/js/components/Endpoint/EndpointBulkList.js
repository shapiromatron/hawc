import React, { Component, PropTypes } from 'react';

import h from '../../utils/helpers';
// import EndpointDetailEdit from './EndpointDetailEdit';
import EndpointBulkForm from '../../containers/EndpointBulkForm';

export default class EndpointBulkList extends Component {

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
    groupEndpoints(endpoint){
        let field = endpoint.field;
        return _.groupBy(endpoint.items, (endpoint) => {
            return endpoint[field];
        });
    }

    render() {
        let { endpoint } = this.props,
            field = endpoint.field,
            groupedEndpoints = this.groupEndpoints(endpoint),
            rows = _.map(groupedEndpoints, (endpoints) => {
                return <EndpointBulkForm
                    key={endpoints[0][field] || 'Empty'}
                    items={endpoints}
                    field={field}/>;
            });
        return (
            <div className='container-fluid'>
                <div className='row'>
                    <span className='bulk-header span4'>{h.caseToWords(endpoint.field)}</span>
                    <span className='bulk-header span5'>{h.caseToWords(endpoint.field)} Edit</span>
                    <span className='bulk-header span2'>Submit Edit</span>
                </div>

                    {rows}
            </div>
        );
    }
}

EndpointBulkList.propTypes = {
    endpoint: PropTypes.shape({
        type: PropTypes.string,
        field: PropTypes.string.required,
        items: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.number.isRequired,
                name: PropTypes.string.isRequired,
            }).isRequired
        ),
    }),
};
