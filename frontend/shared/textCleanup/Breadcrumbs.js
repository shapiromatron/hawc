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

        const items = [{text: "Cleanup", action: store.clearModel, active: false}];
        if (hasModel) {
            if (hasField) {
                items.push({
                    text: h.titleCase(store.selectedModel.title),
                    action: store.clearField,
                    active: false,
                });
                items.push({
                    text: `Cleanup ${h.titleCase(store.selectedField)}`,
                    action: null,
                    active: true,
                });
            } else {
                items.push({
                    text: `${h.titleCase(store.selectedModel.title)} Field Selection`,
                    action: null,
                    active: true,
                });
            }
        } else {
            items.push({text: "Model selection", action: null, active: true});
        }

        return (
            <ol className="breadcrumb">
                {items.map((item, i) => {
                    return (
                        <a
                            key={i}
                            href="#"
                            className={`breadcrumb-item ${item.active ? "active" : ""}`}
                            onClick={item.action}>
                            {item.text}
                        </a>
                    );
                })}
            </ol>
        );
    }
}
Breadcrumbs.propTypes = {
    store: PropTypes.object,
};

export default Breadcrumbs;
