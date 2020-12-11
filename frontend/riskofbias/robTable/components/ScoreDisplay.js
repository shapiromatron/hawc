import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";
import ScoreBar from "./ScoreBar";
import {OVERRIDE_SCORE_LABEL_MAPPING} from "../../constants";
import "./ScoreDisplay.css";

@inject("store")
@observer
class CopyScoresButton extends Component {
    render() {
        let {store, score, editableScores} = this.props;
        if (editableScores === undefined || editableScores.length == 0) {
            return null;
        } else if (editableScores.length === 1) {
            return (
                <button
                    className="btn btn-outline-dark float-right"
                    type="button"
                    onClick={() => {
                        store.updateFormState(
                            editableScores[0].id,
                            "notes",
                            editableScores[0].notes + score.notes
                        );
                    }}>
                    <i className="fa fa-clone"></i>&nbsp;Copy
                </button>
            );
        } else if (editableScores.length > 1) {
            return (
                <div className="btn-group float-right">
                    <button
                        className="btn btn-outline-dark dropdown-toggle"
                        data-toggle="dropdown"
                        type="button">
                        Copy
                    </button>
                    <div className="dropdown-menu dropdown-menu-right">
                        {editableScores.map(editableScore => {
                            return (
                                <button
                                    key={editableScore.id}
                                    type="button"
                                    className="dropdown-item"
                                    onClick={e => {
                                        e.preventDefault();
                                        store.updateFormState(
                                            editableScore.id,
                                            "notes",
                                            editableScore.notes + score.notes
                                        );
                                    }}>
                                    Copy into&nbsp;
                                    {editableScore.label || `Score #${editableScore.id}`}
                                </button>
                            );
                        })}
                    </div>
                </div>
            );
        } else {
            throw "Unknown <CopyScoresButton /> state";
        }
    }
}
CopyScoresButton.propTypes = {
    store: PropTypes.object,
    score: PropTypes.object.isRequired,
    editableScores: PropTypes.arrayOf(PropTypes.object).isRequired,
};

class ScoreDisplay extends Component {
    render() {
        let {score, showAuthors, hasOverrides, editableScores} = this.props,
            showRobScore = !h.hideRobScore(score.metric.domain.assessment.id),
            showAuthorDisplay = showAuthors && score.is_default,
            labelText = score.label,
            displayClass =
                score.is_default && hasOverrides
                    ? "score-display default-score-display"
                    : "score-display",
            finalStar = score.final ? <i className="fa fa-star" title="Final review" /> : null,
            hasOverride = score.overridden_objects.length > 0;

        if (score.is_default) {
            labelText = labelText.length > 0 ? labelText : "Overall";
        }

        return (
            <div className={displayClass}>
                <div>
                    {showAuthorDisplay || hasOverrides ? (
                        <p className="mb-1">
                            {showAuthorDisplay ? (
                                <b className="float-right">
                                    {score.author.full_name}
                                    &nbsp;
                                    {finalStar}
                                </b>
                            ) : null}
                            {hasOverrides ? <b>{labelText}</b> : <b>&nbsp;</b>}
                        </p>
                    ) : null}
                    {editableScores ? (
                        <CopyScoresButton score={score} editableScores={editableScores} />
                    ) : null}
                    {showRobScore ? (
                        <ScoreBar
                            score={score.score}
                            shade={score.score_shade}
                            symbol={score.score_symbol}
                            description={score.score_description}
                            direction={score.bias_direction}
                        />
                    ) : null}
                </div>
                <div>
                    <p dangerouslySetInnerHTML={{__html: score.notes}} />
                </div>
                {hasOverride ? (
                    <div>
                        <p>
                            <b>
                                {
                                    OVERRIDE_SCORE_LABEL_MAPPING[
                                        score.overridden_objects[0].content_type_name
                                    ]
                                }
                            </b>
                        </p>
                        <ul>
                            {score.overridden_objects.map(object => {
                                return (
                                    <li key={object.id}>
                                        <a href={object.object_url}>{object.object_name}</a>
                                    </li>
                                );
                            })}
                        </ul>
                    </div>
                ) : null}
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
        overridden_objects: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.number.isRequired,
                object_id: PropTypes.number.isRequired,
                score_id: PropTypes.number.isRequired,
                content_type_name: PropTypes.string.isRequired,
                object_name: PropTypes.string.isRequired,
                object_url: PropTypes.string.isRequired,
            })
        ),
        notes: PropTypes.string.isRequired,
        score_description: PropTypes.string.isRequired,
        score_symbol: PropTypes.string.isRequired,
        score_shade: PropTypes.string.isRequired,
        score: PropTypes.number.isRequired,
        bias_direction: PropTypes.number.isRequired,
        final: PropTypes.bool,
    }).isRequired,
    showAuthors: PropTypes.bool.isRequired,
    hasOverrides: PropTypes.bool.isRequired,
    editableScores: PropTypes.arrayOf(PropTypes.object),
};

export default ScoreDisplay;
