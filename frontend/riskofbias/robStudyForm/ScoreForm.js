import React, {Component} from "react";
import PropTypes from "prop-types";
import ReactQuill from "react-quill";
import {observer, inject} from "mobx-react";

import ScoreIcon from "riskofbias/robTable/components/ScoreIcon";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

import "./ScoreForm.css";
import ScoreOverrideForm from "./ScoreOverrideForm";

class ScoreInput extends Component {
    componentDidMount() {
        const {choices, value, handleChange} = this.props;
        choices.map(c => c.id).includes(value) ? null : handleChange(NaN);
    }
    render() {
        const {scoreId, choices, value, handleChange} = this.props;

        return (
            <>
                <SelectInput
                    id={`${scoreId}-score`}
                    label="Score"
                    choices={choices}
                    multiple={false}
                    value={value}
                    handleSelect={handleChange}
                />
                {isNaN(value) ? null : <ScoreIcon score={value} />}
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
            scoreChoices = store.metrics[score.metric_id].response_values.map(c => {
                return {id: c, label: store.settings.score_metadata.choices[c]};
            }),
            editableMetricHasOverrides = store.editableMetricHasOverrides(score.metric_id),
            direction_choices = Object.entries(store.settings.score_metadata.bias_direction).map(
                kv => {
                    return {id: kv[0], label: kv[1]};
                }
            ),
            showOverrideCreate = score.is_default === true,
            showDelete = score.is_default === false;

        scoreChoices.unshift({id: "", label: "---"});

        return (
            <div className="score-form container-fluid ">
                <div className="row">
                    <div className="col-md-3">
                        {editableMetricHasOverrides ? (
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
                                        metric: score.metric_id,
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

                        {editableMetricHasOverrides ? (
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
                        <div>
                            <ScoreInput
                                scoreId={score.id}
                                choices={scoreChoices}
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
