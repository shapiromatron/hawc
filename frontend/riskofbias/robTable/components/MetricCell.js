import React, {Component} from "react";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";
import {getMultiScoreDisplaySettings} from "../../constants";
import "./MetricCell.css";

class MetricCell extends Component {
    render() {
        let {scores, handleClick} = this.props,
            firstScore = scores[0],
            displaySettings = getMultiScoreDisplaySettings(scores),
            textColor = h.contrastingColor(firstScore.score_shade);

        return (
            <div
                className="score-cell tooltips"
                name={firstScore.metric_name}
                style={displaySettings.reactStyle}
                onClick={() => handleClick(firstScore.domain_name, firstScore.metric_name)}
                data-toggle="tooltip"
                title={firstScore.metric_name}>
                <span className="score-cell-scores-span text-center" style={{color: textColor}}>
                    {displaySettings.symbolText} {displaySettings.directionText}
                </span>
            </div>
        );
    }
}

MetricCell.propTypes = {
    scores: PropTypes.arrayOf(
        PropTypes.shape({
            score_symbol: PropTypes.string.isRequired,
            score_shade: PropTypes.string.isRequired,
            bias_direction: PropTypes.number.isRequired,
            assessment_id: PropTypes.number.isRequired,
            domain_name: PropTypes.string.isRequired,
            metric_name: PropTypes.string.isRequired,
        })
    ).isRequired,
    handleClick: PropTypes.func.isRequired,
};

export default MetricCell;
