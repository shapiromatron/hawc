import {toJS} from "mobx";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import startupPrismaAppRender from "../../summary/Prisma";

@inject("store")
@observer
class PreviewPanel extends Component {
    render() {
        const settings = toJS(this.props.store.subclass.settings),
            data = this.props.store.subclass.data;
        return (
            <div>
                <legend>Preview</legend>
                <p className="form-text text-muted">Preview the settings for this visualization.</p>
                {startupPrismaAppRender(null, settings, data, { asComponent: true, csrf: this.props.store.base.config.csrf })}
            </div>
        );
    }
}
PreviewPanel.propTypes = {
    store: PropTypes.object,
};
export default PreviewPanel;
