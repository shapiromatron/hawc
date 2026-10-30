import PropTypes from "prop-types";
import React from "react";

import Loading from "./Loading";

class WaitLoad extends React.Component {
    constructor(props) {
        super(props);
        this.state = {isReady: false};
    }
    componentDidMount() {
        setTimeout(() => {
            this.setState({isReady: true});
        }, this.props.wait);
    }
    render() {
        if (this.state.isReady) {
            return this.props.children;
        }
        return <Loading />;
    }
}
WaitLoad.propTypes = {
    children: PropTypes.node.isRequired,
    wait: PropTypes.number,
};
WaitLoad.defaultProps = {
    wait: 500,
};

export default WaitLoad;
