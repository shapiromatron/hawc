import PropTypes from "prop-types";
import React from "react";

const DebugBadge = function({text}) {
    if (window.localStorage.getItem("hawc-debug-badge") != "true") {
        return null;
    }
    return <span className="badge badge-dark px-1 mx-1 debug-badge">{text}</span>;
};

DebugBadge.propTypes = {
    text: PropTypes.any,
};

export default DebugBadge;
