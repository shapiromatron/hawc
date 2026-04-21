import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
import h from "shared/utils/helpers";

class ScrollToErrorBox extends Component {
    constructor(props) {
        super(props);
        this.node = React.createRef();
    }
    componentDidMount() {
        if (this.node.current) {
            h.maybeScrollIntoView(this.node.current);
        }
    }
    componentDidUpdate(prevProps) {
        if (this.props.error !== prevProps.error && this.node.current) {
            h.maybeScrollIntoView(this.node.current);
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
        return (
            <div ref={this.node} className="alert alert-danger">
                {error.toString()}
            </div>
        );
    }
}

ScrollToErrorBox.propTypes = {
    error: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};

export default ScrollToErrorBox;
