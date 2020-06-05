import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";

@inject("store")
@observer
class VisualCustomizationPanel extends Component {
    render() {
        return (
            <div>
                <legend>Visualization customization</legend>
                <p className="help-block">Customize the look/feel/layout of the current visual.</p>
            </div>
        );
    }
}
VisualCustomizationPanel.propTypes = {
    store: PropTypes.object,
};
export default VisualCustomizationPanel;
