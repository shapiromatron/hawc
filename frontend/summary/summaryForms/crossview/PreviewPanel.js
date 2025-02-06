import {toJS} from "mobx";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Loading from "shared/components/Loading";

import Crossview from "../../summary/Crossview";

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
                el = $(this.visualRef.current),
                opts = {
                    dev: true,
                    updateSettingFunc: store.changeSetting,
                };
            new Crossview(data, {}).displayAsPreview(el, opts);
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
