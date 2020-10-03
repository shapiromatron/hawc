import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";

import DetailList from "./components/Items/DetailList";
import getModalClass from "shared/utils/getModalClass";

@observer
class GroupedObject extends Component {
    constructor(props) {
        super(props);
        console.log(props.store.model);
        this.modalClass = getModalClass(props.store.model.modal_key);
    }
    render() {
        let {store} = this.props;
        return (
            <div className="stripe row">
                <span className="bulk-element field span4">
                    <button
                        type="button"
                        title="Show/hide all items"
                        className="btn btn-inverse btn-mini"
                        onClick={() => store.toggleExpanded()}>
                        <i
                            className={store.expanded ? "fa fa-minus-square" : "fa fa-plus-square"}
                        />
                    </button>
                    &nbsp;{store.currentValue || "<empty>"} ({store.objects.length})
                </span>
                <span className="form-group bulk-element span5">
                    <input
                        name={store.fieldName}
                        className="form-control"
                        type="text"
                        value={store.editValue}
                        onChange={event => store.updateValue(event.target.value)}
                    />
                </span>
                <span className="bulk-element button span">
                    <button
                        type="button"
                        onClick={() => store.submitChanges()}
                        className="btn btn-primary">
                        {store.expanded ? "Submit selected items" : "Submit bulk edit"}
                    </button>
                </span>
                {store.expanded ? (
                    <p>DETAIL LIST</p>
                ) : // <DetailList
                //     checkedRows={this.state.detailIDs}
                //     items={store.objects}
                //     onDetailChange={this.onDetailChange}
                //     showModal={id => {
                //         this.modalClass.displayAsModal(id);
                //     }}
                // />
                null}
            </div>
        );
    }
}

GroupedObject.propTypes = {
    store: PropTypes.object.isRequired,
};

export default GroupedObject;
