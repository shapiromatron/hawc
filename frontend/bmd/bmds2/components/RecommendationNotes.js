import PropTypes from "prop-types";
import React from "react";

class RecommendationNotes extends React.Component {
    render() {
        const {notes} = this.props;
        return notes ? (
            <p>
                <b>BMD modeler notes:</b> {notes}
            </p>
        ) : null;
    }
}

RecommendationNotes.propTypes = {
    notes: PropTypes.string.isRequired,
};

export default RecommendationNotes;
