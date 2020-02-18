import React, {Component} from "react";
import PropTypes from "prop-types";
import ReactQuill from "react-quill";

import ScoreIcon from "riskofbias/robTable/components/ScoreIcon";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";
import h from "shared/utils/helpers";
import "./ScoreForm.css";
import {SCORE_SHADES, SCORE_TEXT, SCORE_TEXT_DESCRIPTION} from "../../../constants";

class ScoreForm extends Component {
    constructor(props) {
        super(props);
        this.state = {
            id: props.score.id,
            score: props.score.score,
            notes: props.score.notes,
            label: props.score.label,
        };
        this.handleEditorInput = this.handleEditorInput.bind(this);
        this.handleLabelInput = this.handleLabelInput.bind(this);
        this.updateSelectedScore = this.updateSelectedScore.bind(this);
        this.notifyStateChange = this.notifyStateChange.bind(this);
    }

    notifyStateChange() {
        this.props.notifyStateChange(this.state);
    }

    componentWillMount() {
        this.updateSelectedScore(this.props.score.score);
    }

    componentWillUpdate(nextProps, nextState) {
        // update notes if addText is modified
        // (usually by copying notes over from another form)
        if (nextProps.addText !== this.props.addText) {
            this.setState({
                notes: this.state.notes + nextProps.addText,
            });
        }
        // if score notes is changed, change notes to new notes
        if (nextProps.score.notes !== this.props.score.notes) {
            this.setState({
                notes: nextProps.score.notes,
            });
        }
        // if score is changed, change to new score
        if (nextProps.score.score !== this.props.score.score) {
            this.updateSelectedScore(nextProps.score.score);
        }
    }

    updateSelectedScore(score) {
        this.setState(
            {
                score: parseInt(score),
                selectedShade: SCORE_SHADES[score],
                selectedSymbol: SCORE_TEXT[score],
            },
            this.notifyStateChange
        );
        this.validateInput(score, this.state.notes);
    }

    handleEditorInput(event) {
        this.setState({notes: event}, this.notifyStateChange);
        this.validateInput(this.state.score, event);
    }

    handleLabelInput(event) {
        this.setState({label: event.target.value}, this.notifyStateChange);
    }

    validateInput(score, notes) {
        if (this.state.notes.replace(/<\/?[^>]+(>|$)/g, "") == "") {
            this.props.updateNotesRemaining(this.props.score.id, "add");
        } else {
            this.props.updateNotesRemaining(this.props.score.id, "clear");
        }
    }

    render() {
        let {id, score, notes, label} = this.state,
            {assessment_id} = this.props.config,
            {is_default} = this.props.score,
            choices = this.props.robResponseValues.map(d => {
                return {id: parseInt(d), value: SCORE_TEXT_DESCRIPTION[d]};
            }),
            showScoreInput = !h.hideRobScore(parseInt(assessment_id)),
            showOverrideCreate = is_default === true,
            showDelete = is_default === false,
            deleteScoreOverride = () => {
                this.props.deleteScoreOverride({score_id: this.props.score.id});
            };
        return (
            <div className="score-form">
                {showOverrideCreate ? (
                    <button
                        className="btn btn-primary pull-right"
                        type="button"
                        onClick={this.props.createScoreOverride}>
                        <i className="fa fa-plus"></i>&nbsp;Create new override
                    </button>
                ) : null}

                {showDelete ? (
                    <button
                        className="btn btn-danger pull-right"
                        type="button"
                        onClick={deleteScoreOverride}>
                        <i className="fa fa-trash"></i>&nbsp;Delete override
                    </button>
                ) : null}

                {showScoreInput ? (
                    <div>
                        <SelectInput
                            label="Score"
                            choices={choices}
                            id={`${id}-score`}
                            value={score}
                            handleSelect={this.updateSelectedScore}
                        />
                        <ScoreIcon score={score} />
                    </div>
                ) : null}

                {this.props.metricHasOverrides ? (
                    <div>
                        <label className="checkbox">
                            <input type="checkbox" checked={is_default} readOnly={true}></input>
                            Default score
                        </label>
                        <TextInput
                            id={`${id}-label`}
                            label="Label"
                            name={`label-id-${id}`}
                            onChange={this.handleLabelInput}
                            value={label}
                        />
                    </div>
                ) : null}

                <ReactQuill
                    id={`${id}-notes`}
                    value={notes}
                    onChange={this.handleEditorInput}
                    className="score-editor"
                />
            </div>
        );
    }
}

ScoreForm.propTypes = {
    score: PropTypes.shape({
        id: PropTypes.number.isRequired,
        score: PropTypes.number.isRequired,
        notes: PropTypes.string.isRequired,
        is_default: PropTypes.bool.isRequired,
        label: PropTypes.string.isRequired,
        metric: PropTypes.shape({
            name: PropTypes.string.isRequired,
        }).isRequired,
    }).isRequired,
    metricHasOverrides: PropTypes.bool.isRequired,
    updateNotesRemaining: PropTypes.func.isRequired,
    notifyStateChange: PropTypes.func.isRequired,
    createScoreOverride: PropTypes.func.isRequired,
    deleteScoreOverride: PropTypes.func.isRequired,
    robResponseValues: PropTypes.array.isRequired,
    config: PropTypes.shape({
        assessment_id: PropTypes.number.isRequired,
    }),
};

export default ScoreForm;
