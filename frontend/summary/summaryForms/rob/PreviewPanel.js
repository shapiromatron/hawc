import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Loading from "shared/components/Loading";

@inject("store")
@observer
class PreviewPanel extends Component {
    componentDidMount() {
        this.props.store.subclass.checkDataHash();
    }
    renderVisual() {
        const {store} = this.props;
        if (store.subclass.dataFetchRequired) {
            return <Loading />;
        }
        return <p>Visual</p>;
    }
    render() {
        return (
            <div>
                <legend>Preview</legend>
                {this.renderVisual()}
                <p className="form-text text-muted">Preview the settings for this visualization.</p>
            </div>
        );
    }
}
PreviewPanel.propTypes = {
    store: PropTypes.object,
};
export default PreviewPanel;
