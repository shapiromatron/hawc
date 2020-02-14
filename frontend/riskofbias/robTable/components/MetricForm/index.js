import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import ScoreDisplay from "riskofbias/robTable/components/ScoreDisplay";
import ScoreForm from "riskofbias/robTable/components/ScoreForm";
import "./MetricForm.css";

class MetricForm extends Component {
    renderReadOnlyReviewerScoreRow(data) {
        console.log(data);
        let {metric, config} = this.props,
            displayScores = metric.values.filter(score => score.final === false);

        return (
            <div className="score-row">
                {_.map(displayScores, score => {
                    return (
                        <ScoreDisplay
                            key={score.id}
                            score={score}
                            config={config}
                            copyNotes={config.display === "final" ? this.copyNotes : undefined}
                        />
                    );
                })}
            </div>
        );
    }

    render() {
        let {
                metric,
                config,
                updateNotesRemaining,
                notifyStateChange,
                createScoreOverride,
                deleteScoreOverride,
                robResponseValues,
            } = this.props,
            createScoreOverrideFunc = () => {
                createScoreOverride({
                    metric: metric.values[0].metric.id,
                    riskofbias: config.riskofbias.id,
                });
            },
            formatData = function(editableRiskOfBiasId, metric, scores) {
                return {
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
                    hideDescription: metric.values[0].metric.hide_description,
                    metricName: metric.key,
                    metricDescription: metric.values[0].metric.description,
                    metricHasOverrides: _.some(metric.values, el => el.is_default === false),
                };
            },
            data = formatData(config.riskofbias.id, metric, metric.values);

        return (
            <div className="metric-display">
                <h4>{data.metricName}</h4>
                {data.hideDescription ? null : (
                    <div dangerouslySetInnerHTML={{__html: data.metricDescription}} />
                )}
                {config.display === "final" ? this.renderReadOnlyReviewerScoreRow(data) : null}
                {data.editable.map(score => {
                    return (
                        <ScoreForm
                            key={score.id}
                            config={config}
                            score={score}
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

MetricForm.propTypes = {
    metric: PropTypes.shape({
        key: PropTypes.string.isRequired,
        values: PropTypes.arrayOf(
            PropTypes.shape({
                metric: PropTypes.shape({
                    id: PropTypes.number.isRequired,
                    description: PropTypes.string.isRequired,
                    hide_description: PropTypes.bool.isRequired,
                    name: PropTypes.string.isRequired,
                }).isRequired,
                notes: PropTypes.string.isRequired,
            }).isRequired
        ).isRequired,
    }).isRequired,
    config: PropTypes.object,
    robResponseValues: PropTypes.array.isRequired,
    updateNotesRemaining: PropTypes.func.isRequired,
    notifyStateChange: PropTypes.func.isRequired,
    createScoreOverride: PropTypes.func.isRequired,
    deleteScoreOverride: PropTypes.func.isRequired,
};

export default MetricForm;
