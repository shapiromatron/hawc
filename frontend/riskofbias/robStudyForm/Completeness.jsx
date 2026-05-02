import PropTypes from "prop-types";
import React, {Component} from "react";

class Completeness extends Component {
    render() {
        const {number} = this.props,
            className = number > 0 ? "alert alert-danger" : "alert alert-success",
            message =
                number === 0
                    ? "All items complete! Ready to submit."
                    : number === 1
                      ? "1 item still needs input:"
                      : `${number} items still need input:`;
        return (
            <div className={className}>
                <p>{message}</p>
                {number > 0 ? (
                    <ul>
                        <li>
                            Notes are required if the &quot;Not reported&quot; judgment is selected.
                        </li>
                        <li>
                            It is recommended, but not required, to add notes for all other
                            judgments (except for &quot;Not applicable&quot;, which is
                            self-explanatory)
                        </li>
                    </ul>
                ) : null}
            </div>
        );
    }
}

Completeness.propTypes = {
    number: PropTypes.number.isRequired,
};

export default Completeness;
