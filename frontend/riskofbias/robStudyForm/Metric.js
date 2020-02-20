import _ from "lodash";
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
                {editingFinal ? (
                    <MetricScores
                        scores={nonEditableScores}
                        showAuthors={true}
                        metricHasOverrides={metricHasOverrides}
                    />
                ) : null}
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
