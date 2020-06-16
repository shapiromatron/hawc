import React from "react";
import {observer} from "mobx-react";
import PropTypes from "prop-types";

@observer
class HeatmapTemplateRoot extends React.Component {
    render() {
        return (
            <div>
                <h1>Root.</h1>
                <pre>{JSON.stringify(this.props.store.config)}</pre>
            </div>
        );
    }
}
HeatmapTemplateRoot.propTypes = {
    store: PropTypes.object.isRequired,
};

export default HeatmapTemplateRoot;
