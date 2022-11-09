import PropTypes from "prop-types";
import React from "react";

const ActionsButton = props => {
    return (
        <div className={`dropdown btn-group float-right ${props.containerClasses}`}>
            <a className={`dropdown-toggle btn ${props.dropdownClasses}`} data-toggle="dropdown">
                Actions
            </a>
            <div className="dropdown-menu dropdown-menu-right">{props.items}</div>
        </div>
    );
};
ActionsButton.propTypes = {
    containerClasses: PropTypes.string,
    dropdownClasses: PropTypes.string,
    items: PropTypes.arrayOf(PropTypes.element).isRequired,
};
ActionsButton.defaultProps = {
    containerClasses: "",
    dropdownClasses: "btn-primary",
};

const ActionLink = props => {
    return (
        <a className="dropdown-item" href={props.href}>
            {props.icon ? <i className={`fa fa-fw ${props.icon}`}></i> : null}&nbsp;
            {props.label}
        </a>
    );
};
ActionLink.propTypes = {
    href: PropTypes.string.isRequired,
    icon: PropTypes.string,
    label: PropTypes.string.isRequired,
};

const ActionItem = props => {
    return (
        <button className="dropdown-item" type="button" onClick={props.onClick}>
            {props.icon ? <i className={`fa fa-fw ${props.icon}`}></i> : null}&nbsp;
            {props.label}
        </button>
    );
};
ActionItem.propTypes = {
    onClick: PropTypes.func.isRequired,
    icon: PropTypes.string,
    label: PropTypes.string.isRequired,
};

export {ActionItem, ActionLink, ActionsButton};
