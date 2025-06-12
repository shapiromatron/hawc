import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import ExploreHeatmap from "summary/summary/ExploreHeatmap";
import $ from "$";

import {MissingData, RefreshRequired} from "./common";

@inject("store")
@observer
class PreviewPanel extends Component {
    componentDidMount() {
        const {settingsHash, dataset} = this.props.store.base,
            {settings} = this.props.store.subclass;
        const el = document.getElementById(settingsHash);
        if (el) {
            new ExploreHeatmap({settings}, dataset).displayAsPage($(el), {
                dev: true,
            });
        }
    }

    render() {
        const {hasDataset, dataRefreshRequired, settingsHash} = this.props.store.base;
        let content;
        if (!hasDataset) {
            content = <MissingData />;
        } else if (dataRefreshRequired) {
            content = <RefreshRequired />;
        } else {
            content = <div id={settingsHash}>{settingsHash}</div>;
        }
        return (
            <div>
                <legend>Preview</legend>
                <p className="form-text text-muted">Preview the settings for this visualization.</p>
                {content}
            </div>
        );
    }
}
PreviewPanel.propTypes = {
    store: PropTypes.object,
};
export default PreviewPanel;
