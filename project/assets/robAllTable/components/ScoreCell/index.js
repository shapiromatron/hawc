import React, { Component, PropTypes } from 'react';

import './ScoreCell.css';

class ScoreCell extends Component {

    render(){
        let { score } = this.props;
        return (
            <div className='score-cell' style={{backgroundColor: score.score_shade}}>
                {score.score_symbol}
            </div>
        );
    }
}

ScoreCell.propTypes = {
    score: PropTypes.shape({
        score_symbol: PropTypes.string,
        score_shade: PropTypes.string,
    }).isRequired,
};

export default ScoreCell;
