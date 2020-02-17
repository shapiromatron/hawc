import React, {Component} from "react";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";
import ScoreBar from "riskofbias/robTable/components/ScoreBar";
import "./ScoreDisplay.css";

class ScoreDisplay extends Component {
    render() {
        let {score, config, hasOverrides} = this.props,
            showRobScore = !h.hideRobScore(score.metric.domain.assessment.id),
            showAuthorDisplay = config.display === "final" && config.isForm,
            labelText = score.label ? score.label : "<default>";

        return (
            <div className="score-display" ref="display">
                <div className="flex-1">
                    {showAuthorDisplay ? (
                        <p>
                            <b>{score.author.full_name}</b>
                        </p>
                    ) : null}
                    {showRobScore ? (
                        <ScoreBar
                            score={score.score}
                            shade={score.score_shade}
                            symbol={score.score_symbol}
                            description={score.score_description}
                        />
                    ) : null}
                </div>
                <div className="flex-3 score-notes">
                    {hasOverrides ? (
                        <p>
                            <b>{labelText}</b>
                            {score.is_default ? (
                                <span
                                    className="pull-right fa fa-check-square-o"
                                    title="Default score"></span>
                            ) : (
                                <span
                                    className="pull-right fa fa-square-o"
                                    title="Override score"></span>
                            )}
                        </p>
                    ) : null}
                    <p dangerouslySetInnerHTML={{__html: score.notes}} />
                </div>
            </div>
        );
    }
}

ScoreDisplay.propTypes = {
    score: PropTypes.shape({
        author: PropTypes.object.isRequired,
        metric: PropTypes.shape({
            domain: PropTypes.shape({
                assessment: PropTypes.shape({
                    id: PropTypes.number.isRequired,
                }),
            }),
        }),
        is_default: PropTypes.bool.isRequired,
        label: PropTypes.string.isRequired,
        notes: PropTypes.string.isRequired,
        score_description: PropTypes.string.isRequired,
        score_symbol: PropTypes.string.isRequired,
        score_shade: PropTypes.string.isRequired,
        score: PropTypes.number.isRequired,
    }).isRequired,
    config: PropTypes.shape({
        display: PropTypes.string.isRequired,
        isForm: PropTypes.bool.isRequired,
    }),
    hasOverrides: PropTypes.bool.isRequired,
};

export default ScoreDisplay;
