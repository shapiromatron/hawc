import React, { Component, PropTypes } from 'react';

import './ScoreCell.css';

class ScoreCell extends Component {

    handleClick(){
        let { score, handleClick } = this.props;
        handleClick({domain: score.domain_text, metric: score.metric.metric})
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
        score_symbol: PropTypes.string,
        score_shade: PropTypes.string,
    }).isRequired,
    handleClick: PropTypes.func.isRequired,
};

export default ScoreCell;
