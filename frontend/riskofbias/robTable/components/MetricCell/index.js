import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";
import "./MetricCell.css";

const getStyle = function(sortedScores) {
    let shades = _.chain(sortedScores)
        .map(score => score.score_shade)
        .uniq()
        .value();

    if (shades.length == 1) {
        return {backgroundColor: shades[0]};
    } else if (shades.length >= 2) {
        let dim = Math.ceil(50 / shades.length),
            gradients = shades
                .map((shade, idx) => `${shade} ${idx * dim}px, ${shade} ${(idx + 1) * dim}px`)
                .join(", ");
        return {
            background: `repeating-linear-gradient(-45deg, ${gradients})`,
        };
    }
};

class MetricCell extends Component {
    render() {
        let {scores, handleClick} = this.props,
            firstScore = scores[0],
            sortedScores = _.orderBy(scores, "score", "desc");

        if (h.hideRobScore(scores[0].metric.domain.assessment.id)) {
            return <div className="score-cell" />;
        }

        return (
            <div
                className="score-cell"
                name={firstScore.metric.name}
                style={getStyle(sortedScores)}
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
                    {_.chain(sortedScores)
                        .map(score => score.score_symbol)
                        .uniq()
                        .value()
                        .join(" / ")}
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
