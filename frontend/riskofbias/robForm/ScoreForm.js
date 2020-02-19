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
    // constructor(props) {
    //     super(props);
    //     this.handleEditorInput = this.handleEditorInput.bind(this);
    //     this.handleLabelInput = this.handleLabelInput.bind(this);
    //     this.updateSelectedScore = this.updateSelectedScore.bind(this);
    //     this.notifyStateChange = this.notifyStateChange.bind(this);
    // }

    // notifyStateChange() {
    //     this.props.notifyStateChange(this.state);
    // }

    // componentDidMount() {
    //     this.updateSelectedScore(this.props.score.score);
    // }

    // componentWillUpdate(nextProps, nextState) {
    //     // update notes if addText is modified
    //     // (usually by copying notes over from another form)
    //     if (nextProps.addText !== this.props.addText) {
    //         this.setState({
    //             notes: this.state.notes + nextProps.addText,
    //         });
    //     }
    //     // if score notes is changed, change notes to new notes
    //     if (nextProps.score.notes !== this.props.score.notes) {
    //         this.setState({
    //             notes: nextProps.score.notes,
    //         });
    //     }
    //     // if score is changed, change to new score
    //     if (nextProps.score.score !== this.props.score.score) {
    //         this.updateSelectedScore(nextProps.score.score);
    //     }
    // }

    // updateSelectedScore(score) {
    //     this.setState(
    //         {
    //             score: parseInt(score),
    //             selectedShade: SCORE_SHADES[score],
    //             selectedSymbol: SCORE_TEXT[score],
    //         },
    //         this.notifyStateChange
    //     );
    //     this.validateInput(score, this.state.notes);
    // }

    // handleEditorInput(event) {
    //     this.setState({notes: event}, this.notifyStateChange);
    //     this.validateInput(this.state.score, event);
    // }

    // handleLabelInput(event) {
    //     this.setState({label: event.target.value}, this.notifyStateChange);
    // }

    validateInput(score, notes) {
        if (this.state.notes.replace(/<\/?[^>]+(>|$)/g, "") == "") {
            this.props.updateNotesRemaining(this.props.score.id, "add");
        } else {
            this.props.updateNotesRemaining(this.props.score.id, "clear");
        }
    }

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
