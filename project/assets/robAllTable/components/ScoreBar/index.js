import React, { Component, PropTypes } from 'react';
import ReactCSSTransitionGroup from 'react-addons-css-transition-group';

import './ScoreBar.css';

class ScoreBar extends Component {

    render_score_bar(){
        let { shade, symbol, score } = this.props,
            bar_width = d3.max([d3.round(score / 4 * 100, 2), 15]);
        return (
            <div className='rob_score_bar'
                style={{backgroundColor: shade, width: bar_width+'%'}}>
                <span className='score-symbol'>{symbol}</span>
            </div>
        );
    }

    render() {
        let { description } = this.props;
        return (
            <div className='score-bar'>
                <ReactCSSTransitionGroup
                    transitionName='bar'
                    transitionEnterTimeout={500}>
                    {this.render_score_bar()}
                </ReactCSSTransitionGroup>
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
