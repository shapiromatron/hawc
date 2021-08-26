import React, {Component} from "react";
import PropTypes from "prop-types";

class HelpText extends Component {
    render() {
        return <p className="form-text text-muted">{this.props.text}</p>;
    }
}

HelpText.propTypes = {
    text: PropTypes.string,
};

export default HelpText;
