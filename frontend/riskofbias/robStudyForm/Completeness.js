import React, {Component} from "react";
import PropTypes from "prop-types";

class Completeness extends Component {
    render() {
        let display =
            this.props.number > 0 ? (
                <div className="alert alert-danger">
                    <p>{this.props.number} note(s) still need input.</p>
                    <p>
                        Notes should only be left blank if &quot;Not applicable&quot; judgement is
                        selected.
                    </p>
                </div>
            ) : null;
        return display;
    }
}

Completeness.propTypes = {
    number: PropTypes.number.isRequired,
};

export default Completeness;
