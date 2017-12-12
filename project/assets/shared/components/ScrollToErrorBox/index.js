import React, { Component } from 'react';
import PropTypes from 'prop-types';
import ReactDOM from 'react-dom';
import _ from 'lodash';

class ScrollToErrorBox extends Component {
    componentDidMount() {
        let node = ReactDOM.findDOMNode(this);
        if (node) {
            node.scrollIntoView(false);
        }
    }

    render() {
        let { error } = this.props;

        if (_.isNull(error)) {
            error = null;
        } else if (error.hasOwnProperty('detail')) {
            error = error.detail;
        } else if (error.hasOwnProperty('message')) {
            error = error.message;
        }

        if (!error) {
            return null;
        }

        return <div className="alert alert-danger">{error.toString()}</div>;
    }
}

ScrollToErrorBox.propTypes = {
    error: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};

export default ScrollToErrorBox;
