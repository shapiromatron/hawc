import React, { Component } from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';

import ScoreDisplay from 'riskofbias/robTable/components/ScoreDisplay';
import ScoreForm from 'riskofbias/robTable/components/ScoreForm';
import './MetricForm.css';

class MetricForm extends Component {
    constructor(props) {
        super(props);
        this.state = { addText: '' };
        this.copyNotes = this.copyNotes.bind(this);
    }

    copyNotes(text) {
        this.setState({ addText: text });
    }

    renderScoreRow() {
        let { metric, config } = this.props,
            displayScores = _.filter(metric.values, (score) => {
                return !score.final;
            });

        return (
            <div className="score-row">
                {_.map(displayScores, (score) => {
                    return (
                        <ScoreDisplay
                            key={score.id}
                            score={score}
                            config={config}
                            copyNotes={config.display === 'final' ? this.copyNotes : undefined}
                        />
                    );
                })}
            </div>
        );
    }

    render() {
        let { metric, config, updateNotesLeft, robResponseValues } = this.props,
            formScore = _.find(metric.values, {
                riskofbias_id: parseInt(config.riskofbias.id),
            });

        return (
            <div className="metric-display">
                <h4>{metric.key}</h4>
                <span
                    dangerouslySetInnerHTML={{
                        __html: metric.values[0].metric.description,
                    }}
                />
                {config.display === 'final' ? this.renderScoreRow() : null}
                <ScoreForm
                    ref="form"
                    score={formScore}
                    addText={this.state.addText}
                    updateNotesLeft={updateNotesLeft}
                    robResponseValues={robResponseValues}
                />
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
};

export default MetricForm;
