import React from "react";
import _ from "lodash";
import PropTypes from "prop-types";

class FormFieldError extends React.Component {
    render() {
        if (_.isUndefined(this.props.errors)) return null;
        return (
            <div>
                {this.props.errors.map(function(d, i) {
                    return (
                        <p key={i} className="help-block">
                            <strong>{d}</strong>
                        </p>
                    );
                })}
            </div>
        );
    }
}

FormFieldError.propTypes = {
    errors: PropTypes.object,
};

export default FormFieldError;
