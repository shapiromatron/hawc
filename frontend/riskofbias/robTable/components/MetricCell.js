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
            textColor = String.contrasting_color(firstScore.score_shade);
        if (h.hideRobScore(scores[0].assessment_id)) {
            return <div className="score-cell" />;
        }
        return (
            <div
                className="score-cell"
                name={firstScore.metric_name}
                style={displaySettings.reactStyle}
                onClick={() => handleClick(firstScore.domain_name, firstScore.metric_name)}>
                <span
                    className="score-cell-scores-span tooltips text-center"
                    data-toggle="tooltip"
                    style={{
                        color: textColor,
                    }}
                    title={firstScore.metric_name}>
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
            domain_name: PropTypes.string.isRequired,
        })
    ).isRequired,
    handleClick: PropTypes.func.isRequired,
};

export default MetricCell;
