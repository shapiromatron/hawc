import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";

class FormActions extends Component {
    render() {
        const {isForm, handleSubmit, submitIcon, submitText, cancel, cancelIcon, cancelText} =
            this.props;
        return (
            <div className="form-actions">
                <button
                    type={isForm ? "submit" : "button"}
                    className="btn btn-primary"
                    onClick={handleSubmit}>
                    <i className={`fa fa-fw ${submitIcon}`}></i>&nbsp;
                    {submitText}
                </button>
                &emsp;
                {_.isString(cancel) ? (
                    <a role="button" className="btn btn-secondary" href={cancel}>
                        <i className="fa fa-fw fa-times"></i> {cancelText}
                    </a>
                ) : null}
                {_.isFunction(cancel) ? (
                    <button type="button" className="btn btn-secondary" onClick={cancel}>
                        <i className={`fa fa-fw ${cancelIcon}`}></i> {cancelText}
                    </button>
                ) : null}
            </div>
        );
    }
}

FormActions.propTypes = {
    isForm: PropTypes.bool,
    handleSubmit: PropTypes.func,
    submitIcon: PropTypes.string,
    submitText: PropTypes.string,
    cancel: PropTypes.oneOfType([PropTypes.string, PropTypes.func]),
    cancelIcon: PropTypes.string,
    cancelText: PropTypes.string,
};

FormActions.defaultProps = {
    isForm: false,
    submitIcon: "fa-save",
    submitText: "Save",
    cancelIcon: "fa-times",
    cancelText: "Cancel",
};

export default FormActions;
