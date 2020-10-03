import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import h from "shared/utils/helpers";

@inject("store")
@observer
class Breadcrumbs extends Component {
    render() {
        const {store} = this.props,
            hasModel = store.selectedModel !== null,
            hasField = store.selectedField !== null;

        return (
            <ul className="breadcrumb">
                <li className="active">
                    <a href="#" onClick={store.clearModel}>
                        Cleanup
                    </a>
                    <span className="divider">/</span>
                </li>

                {hasModel ? (
                    <li>
                        <a href="#" onClick={store.clearField}>
                            {h.titleCase(store.selectedModel.title)}
                        </a>
                        <span className="divider">/</span>
                    </li>
                ) : (
                    <li className="active">
                        Select model
                        <span className="divider">/</span>
                    </li>
                )}

                {hasField ? (
                    <li className="active">
                        {h.titleCase(store.selectedField)}
                        <span className="divider">/</span>
                    </li>
                ) : null}
            </ul>
        );
    }
}
Breadcrumbs.propTypes = {
    store: PropTypes.object,
};

export default Breadcrumbs;
