import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";

import MetricScores from "./MetricScores";
import "./MetricDisplay.css";

class MetricDisplay extends Component {
    render() {
        const {metric, config} = this.props,
            scores = metric.values.filter(score => {
                return config.display === "all" ? true : score.final;
            }),
            metricHasOverrides = _.chain(scores)
                .map(score => score.is_default === false)
                .some()
                .value(),
            showAuthors = config.display === "all";

        return (
            <div className="metric-display">
                <h4>{scores[0].metric.name}</h4>
                {scores[0].metric.hide_description ? null : (
                    <div dangerouslySetInnerHTML={{__html: scores[0].metric.description}} />
                )}
                <MetricScores
                    scores={scores}
                    showAuthors={showAuthors}
                    metricHasOverrides={metricHasOverrides}
                />
            </div>
        );
    }
}

MetricDisplay.propTypes = {
    metric: PropTypes.shape({
        key: PropTypes.string.isRequired,
        values: PropTypes.arrayOf(
            PropTypes.shape({
                notes: PropTypes.string.isRequired,
                score_description: PropTypes.string.isRequired,
                score_symbol: PropTypes.string.isRequired,
                score_shade: PropTypes.string.isRequired,
            }).isRequired
        ).isRequired,
    }).isRequired,
    config: PropTypes.shape({
        display: PropTypes.string.isRequired,
        isForm: PropTypes.bool.isRequired,
    }),
};

export default MetricDisplay;
