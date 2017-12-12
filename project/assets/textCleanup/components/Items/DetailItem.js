import React, { Component } from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';

class DetailItem extends Component {
    render() {
        let { fields, item } = this.props,
            checked = _.includes(this.props.checkedRows, item.id);
        return (
            <div className="detail-stripe">
                {_.map(fields, (field) => {
                    return (
                        <span
                            key={field}
                            id={item.id}
                            className="detail-item"
                            onClick={this.props.showModal}
                        >
                            {item[field] || 'N/A'}
                        </span>
                    );
                })}
                <span className="detail-item">
                    <input
                        type="checkbox"
                        title="Include/exclude selected object in change"
                        checked={checked}
                        id={item.id}
                        onChange={this.props.onDetailChange}
                    />
                </span>
            </div>
        );
    }
}

DetailItem.propTypes = {
    onDetailChange: PropTypes.func.isRequired,
    showModal: PropTypes.func.isRequired,
    checkedRows: PropTypes.array,
    item: PropTypes.object.isRequired,
    fields: PropTypes.array.isRequired,
};

export default DetailItem;
