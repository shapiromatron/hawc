import React, {Component} from "react";
import PropTypes from "prop-types";
import {VelocityComponent} from "velocity-react";

import {
    SCORE_BAR_WIDTH_PERCENTAGE,
    BIAS_DIRECTION_SIMPLE,
    BIAS_DIRECTION_VERBOSE,
    BIAS_DIRECTION_UNKNOWN,
} from "riskofbias/constants";

import "./ScoreBar.css";

class ScoreBar extends Component {
    render_score_bar() {
        let {shade, symbol} = this.props;
        return (
            <div className="rob_score_bar" style={{backgroundColor: shade, opacity: 0, width: 0}}>
                <span style={{color: String.contrasting_color(shade)}} className="score-symbol">
                    {symbol}
                </span>
            </div>
        );
    }

    render() {
        let {description, direction, score} = this.props,
            direction_postfix = " | Bias direction " + BIAS_DIRECTION_VERBOSE[direction],
            barWidth = SCORE_BAR_WIDTH_PERCENTAGE[score];

        return (
            <div className="score-bar">
                <VelocityComponent
                    animation={{opacity: 1, width: `${barWidth}%`}}
                    runOnMount={true}
                    duration={1000}>
                    {this.render_score_bar()}
                </VelocityComponent>
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
