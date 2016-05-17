import React, { Component, PropTypes } from 'react';

import ScoreBar from 'robTable/components/ScoreBar';
import './ScoreDisplay.css';


class ScoreDisplay extends Component {

    render(){
        let { score } = this.props;
        return (
            <div className='score-display'>
                <h5>{score.author}</h5>
                <ScoreBar score={score.score}
                          shade={score.score_shade}
                          symbol={score.score_symbol}
                          description={score.score_description}/>
                <hr/>
                <span dangerouslySetInnerHTML={{
                    __html: score.notes,
                }} />
            </div>
        );
    }
}

ScoreDisplay.propTypes = {
    score: PropTypes.shape({
        author: PropTypes.string.isRequired,
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
    }).isRequired,
};

export default ScoreDisplay;
