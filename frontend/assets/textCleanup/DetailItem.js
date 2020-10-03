import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";

import getModalClass from "shared/utils/getModalClass";

@observer
class DetailItem extends Component {
    render() {
        let {store, item} = this.props;
        return (
            <div className="detail-stripe">
                {store.fieldNames.map(field => {
                    return (
                        <span
                            key={field}
                            id={item.id}
                            className="detail-item"
                            onClick={() => {
                                const key = store.model.modal_key,
                                    modalClass = getModalClass(key);
                                if (modalClass) {
                                    modalClass.displayAsModal(item.id);
                                } else {
                                    console.error("Modal class not found", key);
                                }
                            }}>
                            {item[field] || "<empty>"}
                        </span>
                    );
                })}
                <span className="detail-item">
                    <input
                        type="checkbox"
                        title="Include/exclude selected object in change"
                        checked={store.selectedObjects.has(item.id)}
                        onChange={() => store.toggleSelectItem(item.id)}
                    />
                </span>
            </div>
        );
    }
}

DetailItem.propTypes = {
    item: PropTypes.object.isRequired,
    store: PropTypes.object.isRequired,
};

export default DetailItem;
