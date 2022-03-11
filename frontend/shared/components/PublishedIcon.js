import React from "react";
import PropTypes from "prop-types";

const PublishedIcon = props => {
    return props.isPublished ? (
        <i
            title="Published (visible to the public)"
            className="fa fa-fw fa-eye"
            aria-hidden="true"></i>
    ) : (
        <i
            title="Unpublished (not be visible to the public and in some visualizations)"
            className="fa fa-fw fa-eye-slash"
            aria-hidden="true"></i>
    );
};

PublishedIcon.propTypes = {
    isPublished: PropTypes.bool.isRequired,
    showPublished: PropTypes.bool,
};

PublishedIcon.defaultProps = {
    showActions: true,
};

export default PublishedIcon;
