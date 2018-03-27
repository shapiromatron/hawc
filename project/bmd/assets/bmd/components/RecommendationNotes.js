import React from 'react';
import PropTypes from 'prop-types';

class RecommendationNotes extends React.Component {
    render() {
        return (
            <p>
                <b>BMD modeler notes:</b> {this.props.notes}
            </p>
        );
    }
}

RecommendationNotes.propTypes = {
    notes: PropTypes.string.isRequired,
};

export default RecommendationNotes;
