import _ from "lodash";
import React from "react";
import PropTypes from "prop-types";
import ReactDOM from "react-dom";

import MetricScores from "./MetricScores";

const CrossStudyDisplay = props => {
    let {scores} = props,
        metricHasOverrides = _.filter(scores, score => score.is_default === false).length > 0,
        scoresByStudy = _.groupBy(scores, score => score.study.id),
        metric = scores[0].metric,
        domain = scores[0].metric.domain;

    return (
        <div className="cross-study-display">
            <h3>{domain.name}</h3>
            <h4>{metric.name}</h4>
            {metric.hide_description ? null : (
                <div dangerouslySetInnerHTML={{__html: metric.description}} />
            )}
            {_.map(scoresByStudy, scores => {
                const firstScore = scores[0];

                return (
                    <div key={firstScore.id}>
                        <h4>
                            <a
                                target="_blank"
                                rel="noopener noreferrer"
                                href={firstScore.study.url}>
                                {firstScore.study.short_citation}
                            </a>
                        </h4>
                        <MetricScores
                            scores={scores}
                            showAuthors={false}
                            metricHasOverrides={metricHasOverrides}
                        />
                    </div>
                );
            })}
        </div>
    );
};

CrossStudyDisplay.propTypes = {
    scores: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number.isRequired,
            metric: PropTypes.shape({
                name: PropTypes.string.isRequired,
                hide_description: PropTypes.bool.isRequired,
                description: PropTypes.string.isRequired,
                domain: PropTypes.shape({
                    name: PropTypes.string.isRequired,
                }).isRequired,
            }).isRequired,
            study: PropTypes.shape({
                id: PropTypes.number.isRequired,
                url: PropTypes.string.isRequired,
                short_citation: PropTypes.string.isRequired,
            }).isRequired,
            author: PropTypes.object.isRequired,
            notes: PropTypes.string,
            score_description: PropTypes.string.isRequired,
            score_symbol: PropTypes.string.isRequired,
            score_shade: PropTypes.string.isRequired,
        })
    ).isRequired,
};

export function renderCrossStudyDisplay(scores, element) {
    ReactDOM.render(<CrossStudyDisplay scores={scores} />, element);
}

export default CrossStudyDisplay;
