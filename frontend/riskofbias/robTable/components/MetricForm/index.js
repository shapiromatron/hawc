import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import ScoreDisplay from "riskofbias/robTable/components/ScoreDisplay";
import ScoreForm from "riskofbias/robTable/components/ScoreForm";

class MetricForm extends Component {
    renderReadOnlyReviewerScoreRow(data) {
        let {config} = this.props,
            numReviews = data.nonEditable.length,
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
                                        config={config}
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

    formatData() {
        let {metric, config, createScoreOverride} = this.props,
            editableRiskOfBiasId = config.riskofbias.id,
            scores = metric.values;

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
            createScoreOverrideFunc: () => {
                createScoreOverride({
                    metric: metric.values[0].metric.id,
                    riskofbias: config.riskofbias.id,
                });
            },
        };
    }

    render() {
        let {
                config,
                updateNotesRemaining,
                notifyStateChange,
                deleteScoreOverride,
                robResponseValues,
            } = this.props,
            data = this.formatData();

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
                            createScoreOverride={data.createScoreOverrideFunc}
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
