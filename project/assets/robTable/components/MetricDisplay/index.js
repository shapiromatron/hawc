import React, { Component, PropTypes } from 'react';

import ScoreDisplay from 'robTable/components/ScoreDisplay';
import ScoreForm from 'robTable/components/ScoreForm';
import './MetricDisplay.css';


class MetricDisplay extends Component {

    renderScoreRow(){

        let { metric, config } = this.props,
            displayScores;

        if (config.isForm){
            displayScores = _.filter(metric.values, (score) => {return !score.final;});
        } else if (config.display === 'all') {
            displayScores = metric.values;
        } else if (config.display === 'final') {
            displayScores = _.filter(metric.values, (score) => {return score.final;});
        }

        return (
            <div className='score-row'>
            {_.map(displayScores, (score) => {
                return <ScoreDisplay key={score.id} score={score} />;
            })}
            </div>
        );
    }

    renderScoreForm(){
        let formScore = _.findWhere(this.props.metric.values, {riskofbias_id: parseInt(this.props.config.riskofbias.id)});
        return <ScoreForm ref='form' score={formScore} />;
    }

    render(){
        let { metric, config } = this.props;

        return (
            <div className='metric-display'>
                <h4>{metric.key}</h4>
                <span dangerouslySetInnerHTML={{
                    __html: metric.values[0].metric.description,
                }} />
            {(config.isForm && !config.isForm.final) ? null : this.renderScoreRow()}
                {config.isForm ? this.renderScoreForm() : null}
            </div>
        );
    }
}

MetricDisplay.propTypes = {
    metric: PropTypes.shape({
        key: PropTypes.string.isRequired,
        values: PropTypes.arrayOf(
            PropTypes.shape({
                domain_id: PropTypes.number,
                domain_text: PropTypes.string,
                metric: PropTypes.shape({
                    description: PropTypes.string.isRequired,
                    metric: PropTypes.string.isRequired,
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
