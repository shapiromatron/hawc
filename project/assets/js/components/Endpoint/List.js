import React, { Component, PropTypes } from 'react';
import { Link } from 'react-router';
import urls from 'constants/urls';
import BulkList from 'components/Endpoint/BulkList';
import Header from 'components/Endpoint/Header';

export default class EndpointList extends Component {

    render() {
        const { endpoint, params } = this.props;
        return (
            <div className='endpoint_list'>
                <Header params={params} />
                <BulkList endpoint={endpoint} />
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
