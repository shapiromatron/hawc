import React, {Component} from "react";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";
import "./ScoreCell.css";

class ScoreCell extends Component {
    render() {
        let {score, handleClick} = this.props,
            handleClickFn = () => {
                handleClick({domain: score.domain_name, metric: score.metric.name});
            };

        if (h.hideRobScore(score.metric.domain.assessment.id)) {
            return <div className="score-cell" />;
        }

        return (
            <div
                className="score-cell"
                name={score.metric.name}
                style={{backgroundColor: score.score_shade}}
                onClick={handleClickFn}>
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
            domain: PropTypes.shape({
                assessment: PropTypes.shape({
                    id: PropTypes.number.isRequired,
                }),
            }),
        }).isRequired,
    }).isRequired,
    handleClick: PropTypes.func.isRequired,
};

export default ScoreCell;
