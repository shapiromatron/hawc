import React, {Component} from "react";
import PropTypes from "prop-types";
import ReactQuill from "react-quill";
import {observer, inject} from "mobx-react";

import ScoreIcon from "riskofbias/robTable/components/ScoreIcon";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

import h from "shared/utils/helpers";
import "./ScoreForm.css";
import ScoreOverrideForm from "./ScoreOverrideForm";
import {SCORE_TEXT_DESCRIPTION, BIAS_DIRECTION_CHOICES} from "riskofbias/constants";

class ScoreInput extends Component {
    render() {
        const {scoreId, choices, value, handleChange} = this.props,
            scoreChoices = choices.map(d => {
                return {id: parseInt(d), label: SCORE_TEXT_DESCRIPTION[d]};
            });

        return (
            <>
                <SelectInput
                    id={`${scoreId}-score`}
                    label="Score"
                    choices={scoreChoices}
                    multiple={false}
                    value={value}
                    handleSelect={handleChange}
                />
                <ScoreIcon score={value} />
            </>
        );
    }
}
ScoreInput.propTypes = {
    scoreId: PropTypes.number.isRequired,
    choices: PropTypes.arrayOf(PropTypes.number),
    value: PropTypes.number.isRequired,
    handleChange: PropTypes.func.isRequired,
};

class ScoreNotesInput extends Component {
    render() {
        const {scoreId, value, handleChange} = this.props;
        return (
            <ReactQuill
                id={`${scoreId}-notes`}
                value={value}
                onChange={handleChange}
                className="score-editor"
            />
        );
    }
}
ScoreNotesInput.propTypes = {
    scoreId: PropTypes.number.isRequired,
    value: PropTypes.string.isRequired,
    handleChange: PropTypes.func.isRequired,
};

@inject("store")
@observer
class ScoreForm extends Component {
    render() {
        let {scoreId, store} = this.props,
            score = store.getEditableScore(scoreId),
            editableMetricHasOverride = store.editableMetricHasOverride(score.metric.id),
            direction_choices = Object.entries(BIAS_DIRECTION_CHOICES).map(kv => {
                return {id: kv[0], label: kv[1]};
            }),
            showScoreInput = !h.hideRobScore(parseInt(store.config.assessment_id)),
            showOverrideCreate = score.is_default === true,
            showDelete = score.is_default === false;

        return (
            <div className="score-form container-fluid ">
                <div className="row">
                    <div className="col-md-3">
                        {editableMetricHasOverride ? (
                            <TextInput
                                id={`${score.id}-label`}
                                label="Label"
                                name={`label-id-${score.id}`}
                                onChange={e => {
                                    store.updateFormState(scoreId, "label", e.target.value);
                                }}
                                value={score.label}
                            />
                        ) : null}
                    </div>
                    <div className="col-md-9">
                        {showOverrideCreate ? (
                            <button
                                className="btn btn-primary float-right"
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
                                className="btn btn-danger float-right"
                                type="button"
                                onClick={() => store.deleteScoreOverride(scoreId)}>
                                <i className="fa fa-trash"></i>&nbsp;Delete override
                            </button>
                        ) : null}

                        {editableMetricHasOverride ? (
                            score.is_default ? (
                                <b title="Unless otherwise specified, all content will use this value">
                                    <i className="fa fa-check-square-o" />
                                    &nbsp;Default score
                                </b>
                            ) : (
                                <b title="Only selected override content will use this value">
                                    <i className="fa fa-square-o" />
                                    &nbsp;Override score
                                </b>
                            )
                        ) : null}
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-3">
                        {showScoreInput ? (
                            <div>
                                <ScoreInput
                                    scoreId={score.id}
                                    choices={store.study.rob_response_values}
                                    value={score.score}
                                    handleChange={value => {
                                        store.updateFormState(scoreId, "score", parseInt(value));
                                    }}
                                />
                                <SelectInput
                                    id={`${score.id}-direction`}
                                    label="Bias direction"
                                    choices={direction_choices}
                                    multiple={false}
                                    value={score.bias_direction}
                                    handleSelect={value => {
                                        store.updateFormState(
                                            scoreId,
                                            "bias_direction",
                                            parseInt(value)
                                        );
                                    }}
                                />
                            </div>
                        ) : null}
                    </div>
                    <div className="col-md-9">
                        <ScoreNotesInput
                            scoreId={score.id}
                            value={score.notes}
                            handleChange={htmlContent => {
                                store.updateFormState(scoreId, "notes", htmlContent);
                            }}
                        />
                    </div>
                </div>
                {score.is_default ? null : <ScoreOverrideForm score={score} />}
                <hr />
            </div>
        );
    }
}

ScoreForm.propTypes = {
    scoreId: PropTypes.number.isRequired,
    store: PropTypes.object,
};

export {ScoreForm, ScoreInput, ScoreNotesInput};
