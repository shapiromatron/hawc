import React, {Component} from "react";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";
import ScoreBar from "riskofbias/robTable/components/ScoreBar";
import "./ScoreDisplay.css";

class ScoreDisplay extends Component {
    render() {
        let {score, showAuthors, hasOverrides} = this.props,
            showRobScore = !h.hideRobScore(score.metric.domain.assessment.id),
            showAuthorDisplay = showAuthors && score.is_default,
            labelText = score.label,
            displayClass =
                score.is_default && hasOverrides
                    ? "score-display default-score-display"
                    : "score-display",
            finalStar = score.final ? <i className="fa fa-star" title="Final review" /> : null;

        if (score.is_default) {
            labelText = labelText.length > 0 ? `${labelText} (default)` : "Default";
        }

        return (
            <div className={displayClass}>
                <div className="flex-1">
                    {showAuthorDisplay || hasOverrides ? (
                        <p>
                            {showAuthorDisplay ? (
                                <b className="pull-right">
                                    {score.author.full_name}
                                    &nbsp;
                                    {finalStar}
                                </b>
                            ) : null}
                            {hasOverrides ? <b>{labelText}</b> : <b>&nbsp;</b>}
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
    showAuthors: PropTypes.bool.isRequired,
    hasOverrides: PropTypes.bool.isRequired,
};

export default ScoreDisplay;
