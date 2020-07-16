import React, {Component} from "react";
import PropTypes from "prop-types";
import {connect} from "react-redux";

import {submitTaskEdit} from "mgmt/TaskTable/actions";
import TaskForm from "mgmt/TaskTable/components/TaskForm";
import "./TaskToggle.css";

class TaskToggle extends Component {
    constructor(props) {
        super(props);
        this.state = {
            showForm: false,
        };
        this.handleFormDisplay = this.handleFormDisplay.bind(this);
        this.handleLabelDisplay = this.handleLabelDisplay.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleFormDisplay() {
        this.setState({
            showForm: true,
        });
    }

    handleLabelDisplay() {
        this.setState({
            showForm: false,
        });
    }

    handleSubmit() {
        this.props.dispatch(submitTaskEdit(this.form.state));
        this.setState({
            showForm: false,
        });
    }

    renderTaskForm() {
        return (
            <div className={`${this.props.className} relative-parent`}>
                <i
                    onClick={this.handleLabelDisplay}
                    style={{cursor: "pointer"}}
                    title="Cancel edits"
                    className="fa fa-times edit-icon"
                    aria-hidden="true"
                />
                <TaskForm ref={c => (this.form = c)} {...this.props} />
                <button className="btn btn-primary" onClick={this.handleSubmit}>
                    Submit
                </button>
            </div>
        );
    }

    renderTaskLabel() {
        return (
            <div className={`${this.props.className} relative-parent`}>
                <i
                    onClick={this.handleFormDisplay}
                    style={{cursor: "pointer"}}
                    title="Edit this task"
                    className="fa fa-pencil-square-o edit-icon"
                    aria-hidden="true"
                />
                <this.props.TaskLabel task={this.props.task} />
            </div>
        );
    }

    render() {
        return this.state.showForm ? this.renderTaskForm() : this.renderTaskLabel();
    }
}

TaskToggle.propTypes = {
    className: PropTypes.string.isRequired,
    task: PropTypes.object.isRequired,
    TaskLabel: PropTypes.func.isRequired,
    dispatch: PropTypes.func,
};

function mapStateToProps(state) {
    const {autocomplete} = state.config;
    return {
        autocompleteUrl: autocomplete.url,
    };
}

export default connect(mapStateToProps)(TaskToggle);
