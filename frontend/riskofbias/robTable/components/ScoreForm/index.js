import React, {Component} from "react";
import PropTypes from "prop-types";
import ReactQuill from "react-quill";

import ScoreIcon from "riskofbias/robTable/components/ScoreIcon";
import SelectInput from "shared/components/SelectInput";
import h from "shared/utils/helpers";
import "./ScoreForm.css";
import {SCORE_SHADES, SCORE_TEXT, SCORE_TEXT_DESCRIPTION} from "../../../constants";

class ScoreForm extends Component {
    constructor(props) {
        super(props);
        this.state = {
            score: null,
            notes: props.score.notes,
        };
        this.handleEditorInput = this.handleEditorInput.bind(this);
        this.selectScore = this.selectScore.bind(this);
    }

    componentWillMount() {
        this.selectScore(this.props.score.score);
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
            this.selectScore(nextProps.score.score);
        }
    }

    selectScore(score) {
        this.setState({
            score: parseInt(score),
            selectedShade: SCORE_SHADES[score],
            selectedSymbol: SCORE_TEXT[score],
        });
        this.validateInput(score, this.state.notes);
    }

    handleEditorInput(event) {
        this.setState({notes: event});
        this.validateInput(this.state.score, event);
    }

    validateInput(score, notes) {
        if (this.state.notes.replace(/<\/?[^>]+(>|$)/g, "") == "") {
            this.props.updateNotesLeft(this.props.score.id, "add");
        } else {
            this.props.updateNotesLeft(this.props.score.id, "clear");
        }
    }

    render() {
        let {name} = this.props.score.metric,
            {score, notes} = this.state,
            {assessment_id} = this.props.config,
            {is_default, label} = this.props.score,
            choices = this.props.robResponseValues.map(d => {
                return {id: parseInt(d), value: SCORE_TEXT_DESCRIPTION[d]};
            }),
            showScoreInput = !h.hideRobScore(parseInt(assessment_id)),
            showOverrideCreate = is_default === true;

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
                {showScoreInput ? (
                    <div>
                        <SelectInput
                            choices={choices}
                            id={name}
                            value={score}
                            handleSelect={this.selectScore}
                        />
                        <ScoreIcon score={score} />
                    </div>
                ) : null}

                {this.props.metricHasOverrides ? (
                    <div>
                        <label className="checkbox">
                            <input type="checkbox" checked={is_default}></input> Default Score?
                        </label>
                        <label>Label</label>
                        <input value={label}></input>
                    </div>
                ) : null}

                <ReactQuill
                    id={name}
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
        score: PropTypes.number.isRequired,
        notes: PropTypes.string.isRequired,
        is_default: PropTypes.bool.isRequired,
        label: PropTypes.string.isRequired,
        metric: PropTypes.shape({
            name: PropTypes.string.isRequired,
        }).isRequired,
    }).isRequired,
    metricHasOverrides: PropTypes.bool.isRequired,
    updateNotesLeft: PropTypes.func.isRequired,
    createScoreOverride: PropTypes.func.isRequired,
    robResponseValues: PropTypes.array.isRequired,
    config: PropTypes.shape({
        assessment_id: PropTypes.number.isRequired,
    }),
};

export default ScoreForm;
