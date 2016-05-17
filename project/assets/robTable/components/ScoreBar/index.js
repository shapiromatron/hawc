import React, { Component, PropTypes } from 'react';
import ReactCSSTransitionGroup from 'react-addons-css-transition-group';

import './ScoreBar.css';

class ScoreBar extends Component {

    render_score_bar(){
        let { shade, symbol } = this.props;
        return (
            <div className='rob_score_bar'
                style={{backgroundColor: shade}}>
                <span className='score-symbol'>{symbol}</span>
            </div>
        );
    }

    render() {
        let { description, score } = this.props,
            bar_class = d3.max([d3.round(score / 4 * 100, 2), 15]);
        return (
            <div className='score-bar'>
                <ReactCSSTransitionGroup
                    transitionName={`${bar_class}`}
                    transitionEnterTimeout={1000}
                    transitionLeaveTimeout={1000}
                    transitionAppear={true}
                    transitionAppearTimeout={2000}>
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
