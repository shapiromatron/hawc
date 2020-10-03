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
                <div className="row">
                    <span className="bulk-header span4">{h.caseToWords(store.selectedField)}</span>
                    <span className="bulk-header span5">
                        {h.caseToWords(store.selectedField)} edit
                    </span>
                    <span className="bulk-header span2">Submit</span>
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
