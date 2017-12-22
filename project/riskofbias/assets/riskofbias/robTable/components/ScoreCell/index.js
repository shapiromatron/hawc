import React, { Component } from 'react';
import PropTypes from 'prop-types';

import './ScoreCell.css';

class ScoreCell extends Component {
    constructor(props) {
        super(props);
        this.handleClick = this.handleClick.bind(this);
    }

    handleClick() {
        let { score, handleClick } = this.props;
        handleClick({ domain: score.domain_name, metric: score.metric.name });
    }

    render() {
        let { score } = this.props;
        return (
            <div
                className="score-cell"
                name={score.metric.name}
                style={{ backgroundColor: score.score_shade }}
                onClick={this.handleClick}
            >
                <span className="tooltips" data-toggle="tooltip" title={score.metric.name}>
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
            name: PropTypes.string.isRequired,
        }).isRequired,
    }).isRequired,
    handleClick: PropTypes.func.isRequired,
};

export default ScoreCell;
