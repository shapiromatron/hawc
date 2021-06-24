import React, {Component} from "react";
import PropTypes from "prop-types";
import ReactQuill from "react-quill";
import {observer, inject} from "mobx-react";

import ScoreIcon from "riskofbias/robTable/components/ScoreIcon";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";
import h from "shared/utils/helpers";

import {hideScore} from "../constants";
import "./ScoreForm.css";
import ScoreOverrideForm from "./ScoreOverrideForm";

class ScoreInput extends Component {
    constructor(props) {
        super(props);
        this.scoreId = `${h.randomString()}-score`;
    }
    componentDidMount() {
        // special-case if current value doesn't exist in list of valid values;
        // change the value to default (edge-case where response choices change)
        const {choices, value, defaultValue, handleChange} = this.props;
        if (!choices.map(c => c.id).includes(value)) {
            handleChange(defaultValue);
        }
    }
    render() {
        const {choices, value, handleChange} = this.props;
        return (
            <>
                <SelectInput
                    id={this.scoreId}
                    label="Judgement"
                    choices={choices}
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
    choices: PropTypes.arrayOf(PropTypes.object),
    value: PropTypes.number.isRequired,
    handleChange: PropTypes.func.isRequired,
    defaultValue: PropTypes.number.isRequired,
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
        let {score, store} = this.props,
            scoreChoices = store.metrics[score.metric_id].response_values.map(c => {
                return {id: c, label: store.settings.score_metadata.choices[c]};
            }),
            showScoreInput = !hideScore(score.score),
            defaultScoreChoice = store.metrics[score.metric_id].default_response,
            editableMetricHasOverrides = store.editableMetricHasOverrides(score.metric_id),
            direction_choices = Object.entries(store.settings.score_metadata.bias_direction).map(
                kv => {
                    return {id: kv[0], label: kv[1]};
                }
            ),
            showOverrideCreate = score.is_default === true,
            showDelete = score.is_default === false;

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
                                    store.updateScoreState(score, "label", e.target.value);
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
                                onClick={() => store.deleteScoreOverride(score.id)}>
                                <i className="fa fa-trash"></i>&nbsp;Delete override
                            </button>
                        ) : null}

                        {editableMetricHasOverrides ? (
                            score.is_default ? (
                                <b title="Unless otherwise specified, all content will use this value">
                                    <i className="fa fa-check-square-o" />
                                    &nbsp;Default judgement
                                </b>
                            ) : (
                                <b title="Only selected override content will use this value">
                                    <i className="fa fa-square-o" />
                                    &nbsp;Override judgement
                                </b>
                            )
                        ) : null}
                    </div>
                </div>
                <div className="row">
                    {showScoreInput ? (
                        <div className="col-md-3">
                            <ScoreInput
                                choices={scoreChoices}
                                value={score.score}
                                defaultValue={defaultScoreChoice}
                                handleChange={value => {
                                    store.updateScoreState(score, "score", parseInt(value));
                                }}
                            />
                            <SelectInput
                                id={`${score.id}-direction`}
                                label="Bias direction"
                                choices={direction_choices}
                                multiple={false}
                                value={score.bias_direction}
                                handleSelect={value => {
                                    store.updateScoreState(
                                        score,
                                        "bias_direction",
                                        parseInt(value)
                                    );
                                }}
                            />
                        </div>
                    ) : null}
                    <div className="col-md-9">
                        <ScoreNotesInput
                            scoreId={score.id}
                            value={score.notes}
                            handleChange={htmlContent => {
                                store.updateScoreState(score, "notes", htmlContent);
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
    score: PropTypes.object.isRequired,
    store: PropTypes.object,
};

export {ScoreForm, ScoreInput, ScoreNotesInput};
