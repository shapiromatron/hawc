import React, { Component, PropTypes } from 'react';

import ScoreDisplay from 'robAllTable/components/ScoreDisplay';
import './MetricDisplay.css';


class MetricDisplay extends Component {

    render(){
        let { metric } = this.props;
        return (
            <div className='metric-display'>
                <h4>{metric.key}</h4>
                <span dangerouslySetInnerHTML={{
                    __html: metric.values[0].metric.description,
                }} />
                <div className='score-row'>
                    {_.map(metric.values, (score) => {
                        return <ScoreDisplay key={score.id} score={score} />;
                    })}
                </div>
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
};

export default MetricDisplay;
