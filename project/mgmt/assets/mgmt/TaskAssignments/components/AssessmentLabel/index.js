import React, { Component } from 'react';
import PropTypes from 'prop-types';

class AssessmentLabel extends Component {
    render() {
        return (
            <div className={this.props.className}>
                <a href={this.props.assessment.url}>
                    {this.props.assessment.name}
                </a>
            </div>
        );
    }
}

AssessmentLabel.propTypes = {
    assessment: PropTypes.shape({
        name: PropTypes.string.isRequired,
        url: PropTypes.string.isRequired,
        id: PropTypes.number,
    }).isRequired,
};

export default AssessmentLabel;
