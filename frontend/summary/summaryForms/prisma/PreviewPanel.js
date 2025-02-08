import {toJS} from "mobx";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import startupPrismaAppRender from "../../summary/Prisma";

@inject("store")
@observer
class PreviewPanel extends Component {
    render() {
        const {store} = this.props,
            settings = toJS(store.subclass.settings),
            data = store.subclass.data,
            config = store.base.config;
        return (
            <div>
                <legend>Preview</legend>
                <p className="form-text text-muted">Preview the settings for this visualization.</p>
                {startupPrismaAppRender(null, settings, data, config, true)}
            </div>
        );
    }
}
PreviewPanel.propTypes = {
    store: PropTypes.object,
};
export default PreviewPanel;
