import "./ScoreBar.css";

import PropTypes from "prop-types";
import React, {Component} from "react";
import Animation from "shared/components/Animation";
import h from "shared/utils/helpers";

import {
    BIAS_DIRECTION_SIMPLE,
    BIAS_DIRECTION_UNKNOWN,
    BIAS_DIRECTION_VERBOSE,
    SCORE_BAR_WIDTH_PERCENTAGE,
} from "../../constants";

class ScoreBar extends Component {
    render_score_bar() {
        let {shade, symbol, direction} = this.props;
        return (
            <div
                className="rob_score_bar mb-1"
                style={{backgroundColor: shade, opacity: 0, width: 0}}>
                <span style={{color: h.contrastingColor(shade)}} className="score-symbol">
                    {symbol} {BIAS_DIRECTION_SIMPLE[direction]}
                </span>
            </div>
        );
    }

    render() {
        let {description, direction, score} = this.props,
            direction_postfix = " | " + BIAS_DIRECTION_VERBOSE[direction],
            barWidth = SCORE_BAR_WIDTH_PERCENTAGE[score];

        return (
            <div className="score-bar">
                <Animation animation={{opacity: 1, width: `${barWidth}%`}} duration={1000}>
                    {this.render_score_bar()}
                </Animation>
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
