import "./ScoreIcon.css";

import PropTypes from "prop-types";
import React, {Component} from "react";
import h from "shared/utils/helpers";

import {SCORE_SHADES, SCORE_TEXT} from "../../constants";

class ScoreIcon extends Component {
    render() {
        let {score} = this.props,
            textColor = h.contrastingColor(SCORE_SHADES[score]);
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
