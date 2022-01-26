import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import {GroupStore} from "./stores";
import GroupedObject from "./GroupedObject";
import h from "shared/utils/helpers";

@inject("store")
@observer
class GroupedObjectList extends Component {
    render() {
        let {store} = this.props;
        return (
            <div className="container-fluid">
                {store.hasTermMapping ? (
                    <div className="row-fluid">
                        <p className="alert alert-info">
                            <i className="fa fa-exclamation-triangle"></i> Controlled vocabulary may
                            exist for this assessment. This list is filtered to only display terms
                            which are not being used with controlled vocabulary.
                        </p>
                    </div>
                ) : null}
                {store.bulkUpdateError ? (
                    <div className="row-fluid">
                        <p className="alert alert-danger">
                            <i className="fa fa-exclamation-triangle"></i> {store.bulkUpdateError}
                        </p>
                    </div>
                ) : null}
                <div className="row">
                    <span className="bulk-header col-md-4">
                        {h.caseToWords(store.selectedField)}
                    </span>
                    <span className="bulk-header col-md-5">
                        {h.caseToWords(store.selectedField)} edit
                    </span>
                    <span className="bulk-header col-md-2">Submit</span>
                </div>
                {store.groupedObjects.map(items => {
                    const key = items[0][store.selectedField] || "<empty>",
                        groupStore = new GroupStore(
                            store,
                            items,
                            store.selectedModel,
                            store.selectedField
                        );
                    return <GroupedObject key={key} store={groupStore} />;
                })}
            </div>
        );
    }
}

GroupedObjectList.propTypes = {
    store: PropTypes.object,
};

export default GroupedObjectList;
