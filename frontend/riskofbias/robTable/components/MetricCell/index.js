import React, {Component} from "react";
import PropTypes from "prop-types";

import {getMultiScoreDisplaySettings} from "riskofbias/constants";
import h from "shared/utils/helpers";
import "./MetricCell.css";

class MetricCell extends Component {
    render() {
        let {scores, handleClick} = this.props,
            firstScore = scores[0],
            displaySettings = getMultiScoreDisplaySettings(scores);

        if (h.hideRobScore(scores[0].metric.domain.assessment.id)) {
            return <div className="score-cell" />;
        }

        return (
            <div
                className="score-cell"
                name={firstScore.metric.name}
                style={displaySettings.reactStyle}
                onClick={() => {
                    handleClick({
                        domain: firstScore.metric.domain.name,
                        metric: firstScore.metric.name,
                    });
                }}>
                <span
                    className="score-cell-scores-span tooltips text-center"
                    data-toggle="tooltip"
                    title={firstScore.metric.name}>
                    {displaySettings.symbolText}
                    {displaySettings.biasDirection}
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
            metric: PropTypes.shape({
                name: PropTypes.string.isRequired,
                domain: PropTypes.shape({
                    assessment: PropTypes.shape({
                        id: PropTypes.number.isRequired,
                    }),
                }),
            }).isRequired,
        })
    ).isRequired,
    handleClick: PropTypes.func.isRequired,
};

export default MetricCell;
