import React, {Component} from "react";
import PropTypes from "prop-types";

class CancelButton extends Component {
    render() {
        return (
            <button onClick={this.props.onCancel} className="btn space">
                Cancel
            </button>
        );
    }
}

CancelButton.propTypes = {
    onCancel: PropTypes.func.isRequired,
};

export default CancelButton;
