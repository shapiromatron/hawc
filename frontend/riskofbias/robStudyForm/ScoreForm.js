import React, {Component} from "react";
import PropTypes from "prop-types";
import ReactQuill from "react-quill";
import {observer, inject} from "mobx-react";

import ScoreIcon from "riskofbias/robTable/components/ScoreIcon";
import CheckboxInput from "shared/components/CheckboxInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

import h from "shared/utils/helpers";
import "./ScoreForm.css";
import ScoreOverrideForm from "./ScoreOverrideForm";
import {SCORE_TEXT_DESCRIPTION} from "riskofbias/constants";

@inject("store")
@observer
class ScoreForm extends Component {
    render() {
        let {scoreId, store} = this.props,
            score = store.getEditableScore(scoreId),
            editableMetricHasOverride = store.editableMetricHasOverride(score.metric.id),
            choices = store.study.rob_response_values.map(d => {
                return {id: parseInt(d), label: SCORE_TEXT_DESCRIPTION[d]};
            }),
            showScoreInput = !h.hideRobScore(parseInt(store.config.assessment_id)),
            showOverrideCreate = score.is_default === true,
            showDelete = score.is_default === false;

        return (
            <div className="score-form container-fluid ">
                <div className="row-fluid form-inline">
                    <div className="span3">
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
                    <div className="span9">
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

                        {editableMetricHasOverride ? (
                            <CheckboxInput
                                id={`${score.id}-override`}
                                name={"override"}
                                label={score.is_default ? "Default score" : "Override score"}
                                readOnly={true}
                                checked={score.is_default}
                                onChange={() => {}}
                            />
                        ) : null}
                    </div>
                </div>
                <div className="row-fluid">
                    <div className="span3">
                        {showScoreInput ? (
                            <div>
                                <SelectInput
                                    className="span12"
                                    id={`${score.id}-score`}
                                    label="Score"
                                    choices={choices}
                                    multiple={false}
                                    value={score.score}
                                    handleSelect={value => {
                                        store.updateFormState(scoreId, "score", parseInt(value));
                                    }}
                                />
                                <ScoreIcon score={score.score} />
                            </div>
                        ) : null}
                    </div>
                    <div className="span9">
                        <ReactQuill
                            id={`${score.id}-notes`}
                            value={score.notes}
                            onChange={htmlContent => {
                                store.updateFormState(scoreId, "notes", htmlContent);
                            }}
                            className="score-editor"
                        />
                    </div>
                    {score.is_default ? null : <ScoreOverrideForm score={score} />}
                </div>
                <hr />
            </div>
        );
    }
}

ScoreForm.propTypes = {
    scoreId: PropTypes.number.isRequired,
    store: PropTypes.object,
};

export default ScoreForm;
