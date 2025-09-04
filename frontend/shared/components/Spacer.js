import PropTypes from "prop-types";
import React from "react";

const Spacer = ({borderStyle = "8px solid #323a45"}) => {
    return <hr style={{borderTop: borderStyle}} />;
};

Spacer.propTypes = {
    borderStyle: PropTypes.string,
};

export default Spacer;
