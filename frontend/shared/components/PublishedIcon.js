import React from "react";
import PropTypes from "prop-types";

const PublishedIcon = props => {
    const {isPublished, showPublished} = props,
        icon = isPublished ? "fa-eye" : "fa-eye-slash",
        title = isPublished
            ? "Published (visible to the public)"
            : "Unpublished (not be visible to the public and in some visualizations)";

    if (isPublished && !showPublished) {
        return null;
    }

    return <i title={title} className={`fa fa-fw ${icon}`} aria-hidden="true"></i>;
};

PublishedIcon.propTypes = {
    isPublished: PropTypes.bool.isRequired,
    showPublished: PropTypes.bool,
};

PublishedIcon.defaultProps = {
    showPublished: true,
};

export default PublishedIcon;
