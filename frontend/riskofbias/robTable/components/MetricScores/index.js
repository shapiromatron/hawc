import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";

import ScoreDisplay from "../ScoreDisplay";

class MetricScores extends Component {
    render() {
        const {scores, metricHasOverrides, showAuthors} = this.props,
            scoresByRobReview = _.chain(scores)
                .groupBy(score => score.riskofbias_id)
                .values()
                .value(),
            numReviews = scoresByRobReview.length,
            getSpanClass = function(numReviews) {
                if (numReviews <= 1) {
                    return "span12";
                } else if (numReviews === 2) {
                    return "span6";
                } else if (numReviews === 3) {
                    return "span4";
                } else if (numReviews >= 4) {
                    return "span3";
                }
            },
            spanClass = getSpanClass(numReviews);

        if (numReviews === 0) {
            return null;
        }

        return (
            <div className="row-fluid">
                {scoresByRobReview.map((scores, idx) => {
                    return (
                        <div key={idx} className={spanClass}>
                            {scores.map(score => {
                                return (
                                    <ScoreDisplay
                                        key={score.id}
                                        score={score}
                                        showAuthors={showAuthors}
                                        hasOverrides={metricHasOverrides}
                                    />
                                );
                            })}
                        </div>
                    );
                })}
            </div>
        );
    }
}

MetricScores.propTypes = {
    scores: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number.isRequired,
        })
    ),
    showAuthors: PropTypes.bool.isRequired,
    metricHasOverrides: PropTypes.bool.isRequired,
};

export default MetricScores;
