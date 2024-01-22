import "./ScoreBar.css";

import PropTypes from "prop-types";
import React, {Component} from "react";
import h from "shared/utils/helpers";

import {
    BIAS_DIRECTION_SIMPLE,
    BIAS_DIRECTION_UNKNOWN,
    BIAS_DIRECTION_VERBOSE,
    SCORE_BAR_WIDTH_PERCENTAGE,
} from "../../constants";

class ScoreBar extends Component {
    render_score_bar() {
        let {shade, symbol, direction, score} = this.props,
            barWidth = SCORE_BAR_WIDTH_PERCENTAGE[score];
        return (
            <div className="rob_score_bar mb-1" style={{backgroundColor: shade, width: barWidth}}>
                <span style={{color: h.contrastingColor(shade)}} className="score-symbol">
                    {symbol} {BIAS_DIRECTION_SIMPLE[direction]}
                </span>
            </div>
        );
    }

    render() {
        let {description, direction} = this.props,
            direction_postfix = " | " + BIAS_DIRECTION_VERBOSE[direction];

        return (
            <div className="score-bar">
                {this.render_score_bar()}
                <i>{description}</i>
                {direction == BIAS_DIRECTION_UNKNOWN ? null : direction_postfix}
            </div>
        );
    }
}

ScoreBar.propTypes = {
    score: PropTypes.number.isRequired,
    shade: PropTypes.string.isRequired,
    symbol: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
    direction: PropTypes.number.isRequired,
};

export default ScoreBar;
