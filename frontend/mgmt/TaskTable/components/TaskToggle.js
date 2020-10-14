import React, {Component} from "react";
import PropTypes from "prop-types";

import TaskForm from "./TaskForm";
import "./TaskToggle.css";

class TaskToggle extends Component {
    constructor(props) {
        super(props);
        this.state = {
            showForm: false,
        };
    }

    render() {
        const {task, submitTaskEdit, className} = this.props;
        return this.state.showForm ? (
            <div className={`${className} relative-parent`}>
                <i
                    onClick={() => this.setState({showForm: false})}
                    style={{cursor: "pointer"}}
                    title="Cancel edits"
                    className="fa fa-times edit-icon"
                    aria-hidden="true"
                />
                <TaskForm ref={c => (this.form = c)} {...this.props} />
                <button
                    className="btn btn-primary"
                    onClick={() => {
                        submitTaskEdit(this.form.state);
                        this.setState({showForm: false});
                    }}>
                    Submit
                </button>
            </div>
        ) : (
            <div className={`${className} relative-parent`}>
                <i
                    onClick={() => this.setState({showForm: true})}
                    style={{cursor: "pointer"}}
                    title="Edit this task"
                    className="fa fa-pencil-square-o edit-icon"
                    aria-hidden="true"
                />
                <this.props.TaskLabel task={task} />
            </div>
        );
    }
}

TaskToggle.propTypes = {
    className: PropTypes.string.isRequired,
    task: PropTypes.object.isRequired,
    TaskLabel: PropTypes.func.isRequired,
    submitTaskEdit: PropTypes.func.isRequired,
    autocompleteUrl: PropTypes.string.isRequired,
};

export default TaskToggle;
