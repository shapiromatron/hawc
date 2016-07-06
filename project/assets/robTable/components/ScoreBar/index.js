import React, { Component, PropTypes } from 'react';
import { VelocityComponent } from 'velocity-react';

import './ScoreBar.css';

class ScoreBar extends Component {

    render_score_bar(){
        let { shade, symbol } = this.props;
        return (
            <div className='rob_score_bar'
                style={{backgroundColor: shade, opacity: 0, width: 0}}>
                <span className='score-symbol'>{symbol}</span>
            </div>
        );
    }

    render() {
        let { description, score } = this.props,
        // Not Reported score is 10. If Not reported, set barWidth to 25 instead of 250.
            barWidth = score === 10 ? 25 : d3.max([d3.round(score / 4 * 100, 2), 25]);

        return (
            <div className='score-bar'>
                <VelocityComponent animation={{opacity: 1, width: `${barWidth}%`}}
                                   runOnMount={true}
                                   duration={1000}>
                    {this.render_score_bar()}
                </VelocityComponent>
                {description}
            </div>
        );
    }
}

ScoreBar.propTypes = {
    score: PropTypes.number.isRequired,
    shade: PropTypes.string.isRequired,
    symbol: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
};

export default ScoreBar;
