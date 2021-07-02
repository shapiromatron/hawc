import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

import {ScoreForm} from "./ScoreForm";
import MetricScores from "../robTable/components/MetricScores";
import MetricHeader from "../components/MetricDescription";

@inject("store")
@observer
class Metric extends Component {
    render() {
        const {store, metricId} = this.props,
            editableScores = store.getEditableScoresForMetric(metricId),
            nonEditableScores = store.getNonEditableScoresForMetric(metricId),
            metricHasOverrides = store.nonEditableMetricHasOverrides(metricId),
            anyEditableScore = editableScores[0],
            metric = store.metrics[anyEditableScore.metric_id],
            editingFinal = anyEditableScore.final;

        return (
            <div>
                <MetricHeader metric={metric} />
                {editingFinal ? (
                    <MetricScores
                        scores={nonEditableScores}
                        showAuthors={true}
                        metricHasOverrides={metricHasOverrides}
                        editableScores={editableScores}
                    />
                ) : null}
                {editableScores.map(score => {
                    return <ScoreForm key={score.id} score={score} />;
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
