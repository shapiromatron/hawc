import React, {Component} from "react";
import PropTypes from "prop-types";

class Completeness extends Component {
    render() {
        let display =
            this.props.number > 0 ? (
                <div className="alert alert-danger">
                    <p className="mb-0">{this.props.number} note(s) still need input.</p>
                    <ul>
                        <li>
                            Notes are required the &quot;Not reported&quot; judgment is selected.
                        </li>
                        <li>
                            It is recommended, but not required, to add notes for all other
                            judgments (except for &quot;Not applicable&quot; which is
                            self-explanatory)
                        </li>
                    </ul>
                </div>
            ) : (
                <div className="alert alert-success">
                    <p className="mb-0">All items complete! Ready to submit.</p>
                </div>
            );
        return display;
    }
}

Completeness.propTypes = {
    number: PropTypes.number.isRequired,
};

export default Completeness;
