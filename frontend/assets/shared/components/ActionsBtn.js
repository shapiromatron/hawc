import React from "react";
import PropTypes from "prop-types";

const ActionsBtn = props => {
    return (
        <div className={`dropdown btn-group float-right ${props.extraClasses}`}>
            <a className="btn btn-primary dropdown-toggle" data-toggle="dropdown">
                Actions
            </a>
            <div className="dropdown-menu dropdown-menu-right">{props.items}</div>
        </div>
    );
};

ActionsBtn.propTypes = {
    extraClasses: PropTypes.string,
    items: PropTypes.arrayOf(PropTypes.element).isRequired,
};

ActionsBtn.defaultProps = {
    extraClasses: "",
};

export default ActionsBtn;
