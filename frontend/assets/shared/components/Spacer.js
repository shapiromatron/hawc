import React from "react";
import PropTypes from "prop-types";

const Spacer = props => {
    return <hr style={{borderTop: props.borderStyle}} />;
};

Spacer.propTypes = {
    borderStyle: PropTypes.string,
};
Spacer.defaultProps = {
    borderStyle: "8px solid #323a45",
};

export default Spacer;
