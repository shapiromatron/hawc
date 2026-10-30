import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import MetricHeader from "../components/MetricDescription";
import MetricScores from "../robTable/components/MetricScores";
import {ScoreForm} from "./ScoreForm";

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
