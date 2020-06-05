import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";

@inject("store")
@observer
class DataPanel extends Component {
    render() {
        return (
            <div>
                <legend>Data settings</legend>
                <p className="help-block">
                    Settings which change the data which is used to build the heatmap.
                </p>
            </div>
        );
    }
}
DataPanel.propTypes = {
    store: PropTypes.object,
};
export default DataPanel;
