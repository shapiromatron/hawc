import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import h from "shared/utils/helpers";

import DetailItem from "./DetailItem";

@observer
class DetailList extends Component {
    render() {
        const {store} = this.props;
        return (
            <div className="detail-list">
                <div className="detail-header">
                    {store.fieldNames.map(field => {
                        return (
                            <h5 key={field} className="header-field">
                                {h.caseToWords(field)}
                            </h5>
                        );
                    })}
                    <h5 className="header-field" style={{width: "90px"}}>
                        Select all
                        <br />
                        <input
                            type="checkbox"
                            id="all"
                            checked={store.allItemsSelected}
                            onChange={store.toggleSelectAll}
                        />
                    </h5>
                </div>
                {store.objects.map(item => (
                    <DetailItem key={item.id} item={item} store={store} />
                ))}
            </div>
        );
    }
}

DetailList.propTypes = {
    store: PropTypes.object.isRequired,
};

export default DetailList;
