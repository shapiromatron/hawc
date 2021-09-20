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
                    <i className="fa fa-fw fa-save"></i>&nbsp;
                    {submitText}
                </button>
                &ensp;
                <a role="button" className="btn btn-secondary" href={cancelURL}>
                    <i className="fa fa-fw fa-times"></i> Cancel
                </a>
            </div>
        );
    }
}

FormActions.propTypes = {
    isForm: PropTypes.bool,
    handleSubmit: PropTypes.func.isRequired,
    submitText: PropTypes.string,
    cancelURL: PropTypes.string.isRequired,
};

FormActions.defaultProps = {
    isForm: false,
    submitText: "Save",
};

export default FormActions;
