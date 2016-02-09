import React, { Component, PropTypes } from 'react';
import _ from 'underscore';

import h from 'utils/helpers';

export default class DetailList extends Component {

    renderItem(item){
        let fields = _.keys(_.omit(item, ['id', 'ids', 'field', 'showDetails'])),
            checked = _.contains(this.props.checkedRows, item.id);
        return (
            <div key={item.id} className='detail-stripe'>
                {_.map(fields, (field) => {
                    return(
                        <span key={field} id={item.id} className='detail-item' onClick={this.props.showModal}>
                            {item[field] || 'N/A'}
                        </span>
                    );
                })}
                <span className='detail-item'>
                <input type="checkbox"
                       checked={checked}
                       id={item.id}
                       onClick={this.props.onDetailChange}/></span>
            </div>
        );
    }

    render() {
        let { items, field, checkedRows } = this.props,
            fields = _.keys(_.omit(items[0], ['id', 'ids', 'field', 'showDetails'])),
            allChecked = checkedRows ? checkedRows.length === items.length : false;
        return (
            <div className="detail-list">
                <div className="detail-header">
                    {_.map(fields, (field) => {
                        return <h5 key={field} className='header-field'>{h.caseToWords(field)}</h5>;
                    })}
                    <h5 className="header-field">
                    <input type="checkbox" id='all' checked={allChecked} onClick={this.props.onDetailChange}/></h5>
                </div>
                {_.map(_.sortBy(items, 'name'), this.renderItem.bind(this))}
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
