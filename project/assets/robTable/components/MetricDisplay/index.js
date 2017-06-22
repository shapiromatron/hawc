import React, { Component, PropTypes } from 'react';

import ScoreDisplay from 'robTable/components/ScoreDisplay';
import './MetricDisplay.css';


class MetricDisplay extends Component {

    renderScoreRow(){
        let { metric, config } = this.props,
            displayScores = metric.values;

        if (config.display === 'final') {
            displayScores = _.filter(metric.values, (score) => {return score.final;});
        }

        return (
            <div className='score-row'>
            {_.map(displayScores, (score) => {
                return <ScoreDisplay key={score.id} score={score} config={config} />;
            })}
            </div>
        );
    }

    render(){
        let { metric } = this.props;

        return (
            <div className='metric-display'>
                <h4>{metric.key}</h4>
                <span dangerouslySetInnerHTML={{
                    __html: metric.values[0].metric.description,
                }} />
            {this.renderScoreRow()}
            </div>
        );
    }
}

MetricDisplay.propTypes = {
    metric: PropTypes.shape({
        key: PropTypes.string.isRequired,
        values: PropTypes.arrayOf(
            PropTypes.shape({
                metric: PropTypes.shape({
                    description: PropTypes.string.isRequired,
                    name: PropTypes.string.isRequired,
                }).isRequired,
                notes: PropTypes.string.isRequired,
                score_description: PropTypes.string.isRequired,
                score_symbol: PropTypes.string.isRequired,
                score_shade: PropTypes.string.isRequired,
            }).isRequired
        ).isRequired,
    }).isRequired,
    config: PropTypes.object,
};

export default MetricDisplay;
