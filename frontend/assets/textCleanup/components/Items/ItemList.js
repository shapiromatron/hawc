import React, {Component} from "react";
import PropTypes from "prop-types";

import BulkList from "./BulkList";
import Header from "./Header";

class ItemList extends Component {
    render() {
        const {params} = this.props;
        return (
            <div className="endpoint_list">
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
        id: PropTypes.string.isRequired,
        type: PropTypes.string.isRequired,
    }).isRequired,
};

export default ItemList;
