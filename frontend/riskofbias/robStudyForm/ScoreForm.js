import React, {Component} from "react";
import PropTypes from "prop-types";
import ReactQuill from "react-quill";
import {observer, inject} from "mobx-react";

import ScoreIcon from "riskofbias/robTable/components/ScoreIcon";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";
import h from "shared/utils/helpers";
import "./ScoreForm.css";
import {SCORE_TEXT_DESCRIPTION} from "riskofbias/constants";

@inject("store")
@observer
class ScoreForm extends Component {
    render() {
        let {scoreId, metricHasOverrides, store} = this.props,
            score = store.getEditableScore(scoreId),
            choices = store.study.rob_response_values.map(d => {
                return {id: parseInt(d), value: SCORE_TEXT_DESCRIPTION[d]};
            }),
            showScoreInput = !h.hideRobScore(parseInt(store.config.assessment_id)),
            showOverrideCreate = score.is_default === true,
            showDelete = score.is_default === false;

        return (
            <div className="score-form">
                {showOverrideCreate ? (
                    <button
                        className="btn btn-primary pull-right"
                        type="button"
                        onClick={() => {
                            store.createScoreOverride({
                                metric: score.metric.id,
                                riskofbias: score.riskofbias_id,
                            });
                        }}>
                        <i className="fa fa-plus"></i>&nbsp;Create new override
                    </button>
                ) : null}

                {showDelete ? (
                    <button
                        className="btn btn-danger pull-right"
                        type="button"
                        onClick={() => store.deleteScoreOverride(scoreId)}>
                        <i className="fa fa-trash"></i>&nbsp;Delete override
                    </button>
                ) : null}

                {showScoreInput ? (
                    <div>
                        <SelectInput
                            label="Score"
                            choices={choices}
                            id={`${score.id}-score`}
                            value={score.score}
                            handleSelect={value => {
                                score.score = parseInt(value);
                            }}
                        />
                        <ScoreIcon score={score.score} />
                    </div>
                ) : null}

                {metricHasOverrides ? (
                    <div>
                        <label className="checkbox">
                            <input
                                type="checkbox"
                                checked={score.is_default}
                                readOnly={true}></input>
                            Default score
                        </label>
                        <TextInput
                            id={`${score.id}-label`}
                            label="Label"
                            name={`label-id-${score.id}`}
                            onChange={e => {
                                score.label = e.target.value;
                            }}
                            value={score.label}
                        />
                    </div>
                ) : null}

                <ReactQuill
                    id={`${score.id}-notes`}
                    value={score.notes}
                    onChange={htmlContent => {
                        score.notes = htmlContent;
                    }}
                    className="score-editor"
                />
            </div>
        );
    }
}

ScoreForm.propTypes = {
    scoreId: PropTypes.number.isRequired,
    metricHasOverrides: PropTypes.bool.isRequired,
    store: PropTypes.object,
};

export default ScoreForm;
