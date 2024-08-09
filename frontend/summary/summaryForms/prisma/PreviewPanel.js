import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

@inject("store")
@observer
class PreviewPanel extends Component {
    render() {
        const settings = this.props.store.subclass.settings;
        return (
            <div>
                <legend>Preview</legend>
                <p className="form-text text-muted">Preview the settings for this visualization.</p>
                <p>{JSON.stringify(settings)}</p>
            </div>
        );
    }
}
PreviewPanel.propTypes = {
    store: PropTypes.object,
};
export default PreviewPanel;
