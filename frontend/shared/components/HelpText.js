import PropTypes from "prop-types";
import React, {Component} from "react";

class HelpText extends Component {
    render() {
        return <p className="form-text text-muted">{this.props.text}</p>;
    }
}

HelpText.propTypes = {
    text: PropTypes.string,
};

export default HelpText;
