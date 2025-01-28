import {toJS} from "mobx";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Loading from "shared/components/Loading";

import RoBBarchart from "../../summary/RoBBarchart";
import RoBHeatmap from "../../summary/RoBHeatmap";

@inject("store")
@observer
class PreviewPanel extends Component {
    constructor(props) {
        super(props);
        this.visualRef = React.createRef();
    }
    _maybeShowVisual() {
        const store = this.props.store.subclass;
        store.checkDataHash();
        if (this.visualRef.current) {
            const data = toJS(store.visualData),
                el = $(this.visualRef.current);
            // TODO - update legend dragging x/y somehow?
            if (store.isHeatmap) {
                new RoBHeatmap(data, {}).displayAsPreview(el);
            } else if (store.isBarchart) {
                new RoBBarchart(data, {}).displayAsPreview(el);
            }
        }
    }
    componentDidMount() {
        this._maybeShowVisual();
    }
    componentDidUpdate() {
        this._maybeShowVisual();
    }
    renderVisual() {
        const {store} = this.props;
        if (store.subclass.dataFetchRequired) {
            return <Loading />;
        }
        return <div ref={this.visualRef}></div>;
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
