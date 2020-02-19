import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

import ScoreForm from "riskofbias/robTable/components/ScoreForm";
import ScoreDisplay from "riskofbias/robTable/components/ScoreDisplay";

@inject("store")
@observer
class Metric extends Component {
    renderReadOnlyReviewerScoreRow(data) {
        let numReviews = data.nonEditable.length,
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
                {data.nonEditable.map((scores, idx) => {
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
                                        hasOverrides={data.metricHasOverrides}
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
        const {scores, store} = this.props,
            editableRiskOfBiasId = store.config.riskofbias.id,
            assessmentId = store.config.assessment_id,
            updateNotesRemaining = () => console.log("updateNotesRemaining"),
            robResponseValues = store.study.rob_response_values,
            notifyStateChange = store.notifyStateChange,
            createScoreOverride = store.createScoreOverride,
            deleteScoreOverride = store.deleteScoreOverride,
            anyScore = this.props.scores[0],
            name = anyScore.metric.name,
            hideDescription = anyScore.metric.hide_description,
            description = anyScore.metric.description,
            data = {
                metricHasOverrides: _.some(scores, el => el.is_default === false),
                editable: _.chain(scores)
                    .filter(score => score.riskofbias_id === editableRiskOfBiasId)
                    .sortBy("id")
                    .value(),
                nonEditable: _.chain(scores)
                    .filter(score => score.riskofbias_id !== editableRiskOfBiasId)
                    .sortBy("id")
                    .groupBy(score => score.author.id)
                    .values()
                    .value(),
            },
            createScoreOverrideFunc = () => {
                createScoreOverride({
                    metric: anyScore.metric.id,
                    riskofbias: editableRiskOfBiasId,
                });
            },
            editingFinal = data.editable[0].final;

        return (
            <div>
                <h4>{name}</h4>
                {hideDescription ? null : <div dangerouslySetInnerHTML={{__html: description}} />}
                {editingFinal ? this.renderReadOnlyReviewerScoreRow(data) : null}
                {data.editable.map(score => {
                    return (
                        <ScoreForm
                            key={score.id}
                            score={score}
                            assessmentId={assessmentId}
                            updateNotesRemaining={updateNotesRemaining}
                            robResponseValues={robResponseValues}
                            notifyStateChange={notifyStateChange}
                            createScoreOverride={createScoreOverrideFunc}
                            deleteScoreOverride={deleteScoreOverride}
                            metricHasOverrides={data.metricHasOverrides}
                        />
                    );
                })}
            </div>
        );
    }
}

Metric.propTypes = {
    metricId: PropTypes.number.isRequired,
    scores: PropTypes.array.isRequired,
};

export default Metric;
