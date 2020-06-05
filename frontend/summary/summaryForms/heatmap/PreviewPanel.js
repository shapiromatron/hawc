import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";

@inject("store")
@observer
class PreviewPanel extends Component {
    render() {
        return (
            <div>
                <legend>Preview</legend>
                <p className="help-block">Preview the settings for this visualization.</p>
            </div>
        );
    }
}
PreviewPanel.propTypes = {
    store: PropTypes.object,
};
export default PreviewPanel;
