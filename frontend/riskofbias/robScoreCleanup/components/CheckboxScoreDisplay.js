import PropTypes from "prop-types";
import React, {Component} from "react";
import Study from "study/Study";

import {SCORE_SHADES, SCORE_TEXT, SCORE_TEXT_DESCRIPTION} from "../../constants";
import ScoreBar from "../../robTable/components/ScoreBar";

class CheckboxScoreDisplay extends Component {
    render() {
        const {checked, score, handleCheck} = this.props;
        return (
            <div className="row checkbox-score-display-row">
                <div className="score-display-checkbox col-md-3">
                    <p onClick={() => Study.displayAsModal(score.study_id)}>
                        <b>{score.study_name}</b>
                    </p>
                    <input
                        type="checkbox"
                        name="checkbox-score-select"
                        title="Include/exclude selected item in change"
                        checked={checked}
                        id={score.id}
                        onChange={handleCheck}
                    />
                </div>
                <div className="col-md-3">
                    {score.label.length > 0 ? (
                        <p className="mb-1">
                            <b>{score.label}: </b>
                            {score.is_default ? " (overall)" : " (override)"}
                        </p>
                    ) : null}
                    <ScoreBar
                        score={score.score}
                        shade={SCORE_SHADES[score.score]}
                        symbol={SCORE_TEXT[score.score]}
                        description={SCORE_TEXT_DESCRIPTION[score.score]}
                        direction={score.bias_direction}
                    />
                </div>
                <div className="col-md-6">
                    <p dangerouslySetInnerHTML={{__html: score.notes}} />
                </div>
            </div>
        );
    }
}

CheckboxScoreDisplay.propTypes = {
    checked: PropTypes.bool.isRequired,
    handleCheck: PropTypes.func.isRequired,
    score: PropTypes.shape({
        bias_direction: PropTypes.number.isRequired,
        id: PropTypes.number.isRequired,
        is_default: PropTypes.bool.isRequired,
        label: PropTypes.string.isRequired,
        notes: PropTypes.string,
        score: PropTypes.number.isRequired,
        study_id: PropTypes.number.isRequired,
        study_name: PropTypes.string.isRequired,
    }),
};

export default CheckboxScoreDisplay;
