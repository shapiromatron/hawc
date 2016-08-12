import React, { Component, PropTypes } from 'react';

import BulkList from './BulkList';
import Header from './Header';


class ItemList extends Component {

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

ItemList.propTypes = {
    items: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number.isRequired,
            name: PropTypes.string.isRequired,
        }).isRequired
    ).isRequired,
    params: PropTypes.shape({
        field: PropTypes.string.isRequired,
        id: React.PropTypes.string.isRequired,
        type: React.PropTypes.string.isRequired,
    }).isRequired,
};

export default ItemList;
