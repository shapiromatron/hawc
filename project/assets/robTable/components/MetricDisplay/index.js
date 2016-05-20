import React, { Component, PropTypes } from 'react';

import ScoreDisplay from 'robTable/components/ScoreDisplay';
import ScoreForm from 'robTable/components/ScoreForm';
import './MetricDisplay.css';


class MetricDisplay extends Component {

    renderScoreForm(){
        let formScore = _.findWhere(this.props.metric.values, {final: true});
        return <ScoreForm ref='form' score={formScore} />;
    }

    render(){
        let { metric, isForm } = this.props,
            displayScores = isForm ?
                _.filter(metric.values, (score) => {return !score.final;}) :
                metric.values;

        return (
            <div className='metric-display'>
                <h4>{metric.key}</h4>
                <span dangerouslySetInnerHTML={{
                    __html: metric.values[0].metric.description,
                }} />
                <div className='score-row'>
                    {_.map(displayScores, (score) => {
                        return <ScoreDisplay key={score.id} score={score} />;
                    })}
                </div>
                {isForm ? this.renderScoreForm() : null}
                <hr/>
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
    isForm: PropTypes.bool,
};

export default MetricDisplay;
