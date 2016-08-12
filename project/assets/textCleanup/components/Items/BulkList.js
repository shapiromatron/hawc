import React, { Component, PropTypes } from 'react';

import BulkForm from 'textCleanup/containers/Items/BulkForm';
import h from 'textCleanup/utils/helpers';

import './BulkList.css';


class BulkList extends Component {

    // Groups items by the field to be edited.
    groupItems(items, field){
        return _.sortBy(_.groupBy(items, (item) => {
            return item[field];
        }), (item) => {
            return item[0][field];
        });
    }

    render() {
        let { items, params } = this.props,
            field = params.field,
            groupedItems = this.groupItems(items, field);
        return (
            <div className='container-fluid'>
                <div className='row'>
                    <span className='bulk-header span4'>{h.caseToWords(field)}</span>
                    <span className='bulk-header span5'>{h.caseToWords(field)} edit</span>
                    <span className='bulk-header span2'>Submit</span>
                </div>

                    {_.map(groupedItems, (items) => {
                        return <BulkForm
                            key={items[0][field] || 'Empty'}
                            items={items}
                            field={field}/>;
                    })}
            </div>
        );
    }
}

BulkList.propTypes = {
    items: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number.isRequired,
            name: PropTypes.string.isRequired,
        }).isRequired
    ).isRequired,
    params: PropTypes.shape({
        type: PropTypes.string,
        field: PropTypes.string,
        id: PropTypes.string,
    }).isRequired,
};

export default BulkList;
