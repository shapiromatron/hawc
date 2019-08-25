import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { SCORE_SHADES, SCORE_TEXT } from '../../../constants';

import './ScoreIcon.css';

class ScoreIcon extends Component {
    render() {
        let { score } = this.props;
        return (
            <div className="score-icon" style={{ backgroundColor: SCORE_SHADES[score] }}>
                {SCORE_TEXT[score]}
            </div>
        );
    }
}

ScoreIcon.propTypes = {
    score: PropTypes.number.isRequired,
};

export default ScoreIcon;
