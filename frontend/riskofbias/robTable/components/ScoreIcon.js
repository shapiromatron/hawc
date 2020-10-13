import React, {Component} from "react";
import PropTypes from "prop-types";

import {SCORE_SHADES, SCORE_TEXT} from "../../constants";

import "./ScoreIcon.css";

class ScoreIcon extends Component {
    render() {
        let {score} = this.props,
            textColor = String.contrasting_color(SCORE_SHADES[score]);
        return (
            <div
                className="score-icon"
                style={{backgroundColor: SCORE_SHADES[score], color: textColor}}>
                {SCORE_TEXT[score]}
            </div>
        );
    }
}

ScoreIcon.propTypes = {
    score: PropTypes.number.isRequired,
};

export default ScoreIcon;
