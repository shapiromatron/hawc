import React, { Component, PropTypes } from 'react';

import './ScoreCell.css';

class ScoreCell extends Component {

    handleClick(){
        let { score, handleClick } = this.props;
        handleClick({domain: score.domain_name, metric: score.metric.metric});
    }

    render(){
        let { score } = this.props;
        return (
            <div className='score-cell'
                 name={score.metric.metric}
                 style={{backgroundColor: score.score_shade}}
                 onClick={this.handleClick.bind(this)}>
                <span className='tooltips'
                      data-toggle='tooltip'
                      title={score.metric.metric}>
                        {score.score_symbol}
                 </span>
            </div>
        );
    }
}

ScoreCell.propTypes = {
    score: PropTypes.shape({
        score_symbol: PropTypes.string.isRequired,
        score_shade: PropTypes.string.isRequired,
        domain_name: PropTypes.string.isRequired,
        metric: PropTypes.shape({
            metric: PropTypes.string.isRequired,
        }).isRequired,
    }).isRequired,
    handleClick: PropTypes.func.isRequired,
};

export default ScoreCell;
