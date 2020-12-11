import React from "react";
import PropTypes from "prop-types";

class NonFieldErrors extends React.Component {
    render() {
        const {errors} = this.props;

        if (errors && errors.length > 0) {
            return (
                <div className="form-row">
                    <div className="alert alert-warning col-md-12">
                        <p className="mb-2">
                            <b>
                                <i className="fa fa-exclamation-triangle"></i>&nbsp;The following
                                errors were found:
                            </b>
                        </p>
                        <ul className="m-0">
                            {errors.map((error, i) => (
                                <li key={i}>{error}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            );
        }
        return null;
    }
}

NonFieldErrors.propTypes = {
    errors: PropTypes.array,
};

export default NonFieldErrors;
