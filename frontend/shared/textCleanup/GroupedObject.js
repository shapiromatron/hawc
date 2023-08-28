import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import DetailList from "./DetailList";

@observer
class GroupedObject extends Component {
    render() {
        let {store} = this.props;
        return (
            <div className="stripe row">
                <span className="field col-md-4">
                    <button
                        type="button"
                        title="Show/hide all items"
                        className="btn btn-dark btn-sm"
                        onClick={() => store.toggleExpanded()}>
                        <i
                            className={store.expanded ? "fa fa-minus-square" : "fa fa-plus-square"}
                        />
                    </button>
                    &nbsp;{store.currentValue || "<empty>"} ({store.objects.length})
                </span>
                <span className="form-group col-md-5">
                    <textarea
                        name={store.fieldName}
                        className="form-control"
                        type="text"
                        value={store.editValue}
                        onChange={event => store.updateValue(event.target.value)}
                    />
                </span>
                <span>
                    <button
                        type="button"
                        onClick={() => store.submitChanges()}
                        className="btn btn-primary">
                        {store.expanded ? "Submit selected items" : "Submit bulk edit"}
                    </button>
                </span>
                {store.expanded ? <DetailList store={store} /> : null}
            </div>
        );
    }
}

GroupedObject.propTypes = {
    store: PropTypes.object.isRequired,
};

export default GroupedObject;
