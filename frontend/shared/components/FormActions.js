import React, {Component} from "react";
import PropTypes from "prop-types";

class FormActions extends Component {
    render() {
        const {isForm, handleSubmit, submitText, cancelURL} = this.props;
        return (
            <div className="form-actions">
                <button
                    type={isForm ? "submit" : "button"}
                    className="btn btn-primary"
                    onClick={handleSubmit}>
                    {submitText}
                </button>
                &nbsp;
                <a role="button" className="btn btn-secondary" href={cancelURL}>
                    Cancel
                </a>
            </div>
        );
    }
}

FormActions.propTypes = {
    isForm: PropTypes.bool,
    handleSubmit: PropTypes.func,
    submitText: PropTypes.string,
    cancelURL: PropTypes.string.isRequired,
};

FormActions.defaultProps = {
    isForm: false,
    handleSubmit: () => {},
    submitText: "Save",
};

export default FormActions;
