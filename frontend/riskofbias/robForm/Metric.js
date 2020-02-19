import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

import ScoreForm from "./ScoreForm";
import ScoreDisplay from "riskofbias/robTable/components/ScoreDisplay";

@inject("store")
@observer
class Metric extends Component {
    renderReadOnlyReviewerScoreRow(nonEditableScores, metricHasOverrides) {
        let scoresByUser = _.chain(nonEditableScores)
                .groupBy(score => score.author.id)
                .values(),
            numReviews = scoresByUser.length,
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
                {scoresByUser.map((scores, idx) => {
                    return (
                        <div key={idx} className={spanClass}>
                            {scores.map(score => {
                                return (
                                    <ScoreDisplay
                                        key={score.id}
                                        score={score}
                                        config={{
                                            display: "final",
                                            isForm: true,
                                        }}
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

    render() {
        const {store, metricId} = this.props,
            editableRiskOfBiasId = store.config.riskofbias.id,
            assessmentId = store.config.assessment_id,
            anyScore = store.editableScores.filter(score => score.metric.id == metricId)[0],
            name = anyScore.metric.name,
            hideDescription = anyScore.metric.hide_description,
            description = anyScore.metric.description,
            metricHasOverrides = _.chain(store.scores)
                .filter(score => score.metric.id == metricId)
                .map(score => score.is_default === false)
                .some()
                .value(),
            editableScores = store.editableScores.filter(score => score.metric.id == metricId),
            nonEditableScores = store.nonEditableScores.filter(
                score => score.metric.id == metricId
            ),
            editingFinal = editableScores[0].final;

        return (
            <div>
                <h4>{name}</h4>
                {hideDescription ? null : <div dangerouslySetInnerHTML={{__html: description}} />}
                {editingFinal
                    ? this.renderReadOnlyReviewerScoreRow(nonEditableScores, metricHasOverrides)
                    : null}
                {editableScores.map(score => {
                    return (
                        <ScoreForm
                            key={score.id}
                            scoreId={score.id}
                            metricHasOverrides={metricHasOverrides}
                        />
                    );
                })}
            </div>
        );
    }
}

Metric.propTypes = {
    store: PropTypes.object,
    metricId: PropTypes.number.isRequired,
};

export default Metric;
