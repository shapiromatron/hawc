import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";

import {MissingData, RefreshRequired} from "./common";

@inject("store")
@observer
class VisualCustomizationPanel extends Component {
    render() {
        const {hasDataset, dataRefreshRequired} = this.props.store.base;
        let renderMethod;
        if (!hasDataset) {
            renderMethod = this.renderMissingData;
        } else if (dataRefreshRequired) {
            renderMethod = this.renderRefreshRequired;
        } else {
            renderMethod = this.renderForm;
        }
        return (
            <div>
                <legend>Visualization customization</legend>
                <p className="help-block">
                    Customize the look, feel, and layout of the current visual.
                </p>
                {renderMethod()}
            </div>
        );
    }
    renderMissingData() {
        return <MissingData />;
    }
    renderRefreshRequired() {
        return <RefreshRequired />;
    }
    renderForm() {
        return <p>Render form</p>;
    }
}
VisualCustomizationPanel.propTypes = {
    store: PropTypes.object,
};
export default VisualCustomizationPanel;
