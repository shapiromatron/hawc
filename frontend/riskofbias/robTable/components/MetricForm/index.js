import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import ScoreDisplay from "riskofbias/robTable/components/ScoreDisplay";
import ScoreForm from "riskofbias/robTable/components/ScoreForm";
import "./MetricForm.css";

class MetricForm extends Component {
    renderReadOnlyReviewerScoreRow() {
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
                updateNotesLeft,
                createScoreOverride,
                deleteScoreOverride,
                robResponseValues,
            } = this.props,
            hideDescription = metric.values[0].metric.hide_description,
            metricName = metric.key,
            metricDescription = metric.values[0].metric.description,
            metricHasOverrides = _.some(metric.values, el => el.is_default === false),
            createScoreOverrideFunc = () => {
                createScoreOverride({
                    metric: metric.values[0].metric.id,
                    riskofbias: config.riskofbias.id,
                });
            },
            formatData = function(editableRiskOfBiasId, scores) {
                let editable = _.chain(scores)
                        .filter(score => score.riskofbias_id === editableRiskOfBiasId)
                        .sortBy("id")
                        .value(),
                    nonEditable = _.chain(scores)
                        .filter(score => score.riskofbias_id !== editableRiskOfBiasId)
                        .sortBy("id")
                        .groupBy(score => score.author.id)
                        .values()
                        .value();

                return {
                    editable,
                    nonEditable,
                };
            },
            data = formatData(config.riskofbias.id, metric.values);

        return (
            <div className="metric-display">
                <h4>{metricName}</h4>
                {hideDescription ? null : (
                    <div dangerouslySetInnerHTML={{__html: metricDescription}} />
                )}
                {config.display === "final"
                    ? this.renderReadOnlyReviewerScoreRow(data.nonEditable)
                    : null}
                {data.editable.map(score => {
                    return (
                        <ScoreForm
                            key={score.id}
                            config={config}
                            score={score}
                            updateNotesLeft={updateNotesLeft}
                            robResponseValues={robResponseValues}
                            createScoreOverride={createScoreOverrideFunc}
                            deleteScoreOverride={deleteScoreOverride}
                            metricHasOverrides={metricHasOverrides}
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
                    name: PropTypes.string.isRequired,
                }).isRequired,
                notes: PropTypes.string.isRequired,
            }).isRequired
        ).isRequired,
    }).isRequired,
    config: PropTypes.object,
    robResponseValues: PropTypes.array.isRequired,
    updateNotesLeft: PropTypes.func.isRequired,
    createScoreOverride: PropTypes.func.isRequired,
    deleteScoreOverride: PropTypes.func.isRequired,
};

export default MetricForm;
