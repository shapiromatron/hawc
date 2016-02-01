import React, { Component, PropTypes } from 'react';
import { Link } from 'react-router';
import urls from '../../constants/urls';
import EndpointBulkEdit from './EndpointBulkEdit';
import EndpointHeader from './EndpointHeader';

export default class EndpointList extends Component {

    render() {
        const { endpoint, params } = this.props;
        return (
            <div className='endpoint_list'>
                <EndpointHeader params={params} />
                <EndpointBulkEdit endpoint={endpoint} />
            </div>
        );
    }
}

EndpointList.propTypes = {
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
