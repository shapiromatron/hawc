import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

import ScoreForm from "./ScoreForm";
import MetricScores from "riskofbias/robTable/components/MetricScores";

@inject("store")
@observer
class Metric extends Component {
    render() {
        const {store, metricId} = this.props,
            editableScores = store.getEditableScoresForMetric(metricId),
            nonEditableScores = store.getNonEditableScoresForMetric(metricId),
            metricHasOverrides = store.metricHasOverrides(metricId),
            anyEditableScore = editableScores[0],
            name = anyEditableScore.metric.name,
            hideDescription = anyEditableScore.metric.hide_description,
            description = anyEditableScore.metric.description,
            editingFinal = anyEditableScore.final;

        return (
            <div>
                <h4>{name}</h4>
                {hideDescription ? null : <div dangerouslySetInnerHTML={{__html: description}} />}
                {editingFinal ? (
                    <MetricScores
                        scores={nonEditableScores}
                        showAuthors={true}
                        metricHasOverrides={metricHasOverrides}
                    />
                ) : null}
                {editableScores.map(score => {
                    return <ScoreForm key={score.id} scoreId={score.id} />;
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
