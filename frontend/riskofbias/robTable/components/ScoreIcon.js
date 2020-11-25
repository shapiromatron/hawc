import React, {Component} from "react";
import PropTypes from "prop-types";

import {SCORE_SHADES, SCORE_TEXT_JSX, BIAS_DIRECTION_SIMPLE_JSX} from "../../constants";

import "./ScoreIcon.css";

class ScoreIcon extends Component {
    render() {
        let {score, direction} = this.props,
            textColor = String.contrasting_color(SCORE_SHADES[score]);
        return (
            <div
                className="score-icon"
                style={{backgroundColor: SCORE_SHADES[score], color: textColor}}>
                {SCORE_TEXT_JSX[score]}
                {direction ? <>&nbsp;{BIAS_DIRECTION_SIMPLE_JSX[direction]}</> : null}
            </div>
        );
    }
}

ScoreIcon.propTypes = {
    score: PropTypes.number.isRequired,
    direction: PropTypes.number,
};

export default ScoreIcon;
