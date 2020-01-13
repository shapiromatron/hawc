import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import BulkForm from "textCleanup/containers/Items/BulkForm";
import h from "textCleanup/utils/helpers";

import "./BulkList.css";

class BulkList extends Component {
    // Groups items by the field to be edited.
    groupItems(items, field) {
        return _.sortBy(
            _.groupBy(items, item => {
                return item[field];
            }),
            item => {
                return item[0][field];
            }
        );
    }

    render() {
        let {items, params} = this.props,
            groupedItems = this.groupItems(items, params.field);
        return (
            <div className="container-fluid">
                <div className="row">
                    <span className="bulk-header span4">{h.caseToWords(params.field)}</span>
                    <span className="bulk-header span5">{h.caseToWords(params.field)} edit</span>
                    <span className="bulk-header span2">Submit</span>
                </div>

                {_.map(groupedItems, items => {
                    return (
                        <BulkForm
                            key={items[0][params.field] || "Empty"}
                            items={items}
                            params={params}
                        />
                    );
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
        field: PropTypes.string.isRequired,
        id: PropTypes.string.isRequired,
        type: PropTypes.string.isRequired,
    }).isRequired,
};

export default BulkList;
