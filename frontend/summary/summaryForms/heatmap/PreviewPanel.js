import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";

import {MissingData, RefreshRequired} from "./common";

@inject("store")
@observer
class PreviewPanel extends Component {
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
                <legend>Preview</legend>
                <p className="help-block">Preview the settings for this visualization.</p>
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
PreviewPanel.propTypes = {
    store: PropTypes.object,
};
export default PreviewPanel;
