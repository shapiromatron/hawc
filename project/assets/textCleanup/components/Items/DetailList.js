import React, { Component, PropTypes } from 'react';

import DetailItem from 'textCleanup/components/Items/DetailItem';
import h from 'textCleanup/utils/helpers';


class DetailList extends Component {

    render() {
        let { items, checkedRows, onDetailChange, showModal } = this.props,
            fields = _.keys(_.omit(items[0], ['id', 'ids', 'field', 'showDetails'])),
            allChecked = checkedRows ? checkedRows.length === items.length : false;
        return (
            <div className="detail-list">
                <div className="detail-header">
                    {_.map(fields, (field) => {
                        return <h5 key={field} className='header-field'>{h.caseToWords(field)}</h5>;
                    })}
                    <h5 className="header-field" style={{width: '90px'}}>Select all
                        <br/>
                        <input type="checkbox" id='all'
                            checked={allChecked}
                            onChange={onDetailChange}/>
                    </h5>
                </div>
                {_.map(_.sortBy(items, 'name'),
                    (item) => {
                        return <DetailItem key={item.id} item={item}
                                    fields={fields}
                                    onDetailChange={onDetailChange}
                                    showModal={showModal}
                                    checkedRows={checkedRows} />})}
            </div>
        );
    }
}

DetailList.propTypes = {
    items: PropTypes.array.isRequired,
    onDetailChange: PropTypes.func.isRequired,
    showModal: PropTypes.func.isRequired,
    checkedRows: PropTypes.array,
};

export default DetailList;
