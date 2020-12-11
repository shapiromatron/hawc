import React, {Component} from "react";
import PropTypes from "prop-types";
import {toJS} from "mobx";

import DueDateLabel from "./DueDateLabel";
import StatusLabel from "./StatusLabel";
import TaskForm from "./TaskForm";
import {TASK_TYPES} from "../constants";

class EditableTask extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isEditing: false,
        };
    }
    render() {
        const {isEditing} = this.state,
            {task, showOwner, userAutocompleteUrl, handleSubmit} = this.props;
        return isEditing ? (
            <div>
                <TaskForm
                    ref={self => (this.form = self)}
                    task={toJS(task)}
                    className={"flex-1"}
                    autocompleteUrl={userAutocompleteUrl}
                />
                <div>
                    <button
                        type="button"
                        className="btn btn-primary"
                        onClick={() => {
                            if (this.form.hasDataChanged()) {
                                handleSubmit(this.form.state);
                            }
                            this.setState({isEditing: false});
                        }}>
                        <i className="fa fa-check"></i>&nbsp;Submit
                    </button>
                    <span>&nbsp;</span>
                    <button
                        type="button"
                        className="btn btn-light"
                        onClick={() => this.setState({isEditing: false})}>
                        <i className="fa fa-times"></i>&nbsp;Cancel
                    </button>
                </div>
            </div>
        ) : (
            <div className="row">
                <div className="col-md-auto">
                    <StatusLabel task={task} />
                    {showOwner && task.owner ? (
                        <div>
                            <b>Owner: </b>
                            <span>{task.owner.full_name}</span>
                        </div>
                    ) : null}
                    <div>
                        <b>Task: </b>
                        <span>{TASK_TYPES[task.type]}</span>
                    </div>
                    <DueDateLabel status={task.status} due_date={task.due_date} />
                </div>
                <div className="col-md">
                    <button
                        type="button"
                        className="btn btn-light"
                        onClick={() => this.setState({isEditing: true})}>
                        <i
                            title="Edit this task"
                            className="fa fa-pencil-square-o"
                            aria-hidden="true"
                        />
                    </button>
                </div>
            </div>
        );
    }
}

EditableTask.propTypes = {
    task: PropTypes.object.isRequired,
    userAutocompleteUrl: PropTypes.string.isRequired,
    showOwner: PropTypes.bool,
    handleSubmit: PropTypes.func.isRequired,
};

EditableTask.defaultProps = {
    showOwner: true,
};

export default EditableTask;
