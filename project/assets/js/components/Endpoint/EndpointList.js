import React, { Component, PropTypes } from 'react';
import BulkList from 'components/Endpoint/BulkList';
import Header from 'components/Endpoint/Header';

export default class EndpointList extends Component {

    render() {
        const { params } = this.props;
        return (
            <div className='endpoint_list'>
                <Header params={params} />
                <BulkList {...this.props} />
            </div>
        );
    }
}

EndpointList.propTypes = {
    endpoint: PropTypes.shape({
        items: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.number.isRequired,
                name: PropTypes.string.isRequired,
            }).isRequired
        ),
    }),
};
