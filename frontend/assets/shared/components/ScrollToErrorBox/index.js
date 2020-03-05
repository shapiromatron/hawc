import React, {Component} from "react";
import PropTypes from "prop-types";
import ReactDOM from "react-dom";
import _ from "lodash";

class ScrollToErrorBox extends Component {
    componentDidUpdate() {
        // eslint-disable-next-line react/no-find-dom-node
        let node = ReactDOM.findDOMNode(this);
        if (node) {
            node.scrollIntoView(false);
        }
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
