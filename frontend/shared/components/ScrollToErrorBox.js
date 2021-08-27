import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import h from "shared/utils/helpers";

class ScrollToErrorBox extends Component {
    componentDidUpdate() {
        h.maybeScrollIntoView(this);
    }

    render() {
        let {error} = this.props;
        if (_.isNull(error) || error.message === null) {
            error = null;
        } else if (error.detail) {
            error = error.detail;
        }

        if (error === undefined || error === null) {
            return null;
        }

        return <div className="alert alert-danger">{error.toString()}</div>;
    }
}

ScrollToErrorBox.propTypes = {
    error: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};

export default ScrollToErrorBox;
