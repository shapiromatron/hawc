import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import h from "shared/utils/helpers";

@inject("store")
@observer
class Breadcrumbs extends Component {
    render() {
        const {store} = this.props,
            hasModel = store.selectedModel !== null,
            hasField = store.selectedField !== null;

        return (
            <ol className="breadcrumb">
                <li className="breadcrumb-item">
                    <a href="#" onClick={store.clearModel}>
                        Cleanup
                    </a>
                </li>

                {hasModel ? (
                    <li className="breadcrumb-item">
                        <a href="#" onClick={store.clearField}>
                            {h.titleCase(store.selectedModel.title)}
                        </a>
                    </li>
                ) : (
                    <li className="breadcrumb-item active">Model selection</li>
                )}

                {hasField ? (
                    <li className="breadcrumb-item active">
                        Cleanup {h.titleCase(store.selectedField)}
                    </li>
                ) : hasModel ? (
                    <li className="breadcrumb-item active">Field selection</li>
                ) : null}
            </ol>
        );
    }
}
Breadcrumbs.propTypes = {
    store: PropTypes.object,
};

export default Breadcrumbs;
