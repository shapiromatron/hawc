import PropTypes from "prop-types";
import React from "react";

class Alert extends React.Component {
    render() {
        const {className, icon, message} = this.props;
        return (
            <div className={`alert ${className} mb-0`} role="alert">
                {icon ? <i className={`fa fa-fw ${icon} mr-1`}></i> : null}
                {message}
            </div>
        );
    }
}

Alert.propTypes = {
    className: PropTypes.string,
    icon: PropTypes.string,
    message: PropTypes.string,
};
Alert.defaultProps = {
    className: "alert-danger",
    icon: "fa-exclamation-triangle",
    message: "An error ocurred. If the error continues to occur please contact us.",
};

export default Alert;
