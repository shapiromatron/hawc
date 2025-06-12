import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";

class ScrollToErrorBox extends Component {
    componentDidUpdate() {
        // TODO - implement - removed w/ React upgrade to v19
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
