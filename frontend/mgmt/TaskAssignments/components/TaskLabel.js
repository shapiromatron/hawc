import DueDateLabel from "mgmt/TaskTable/components/DueDateLabel";
import StatusLabel from "mgmt/TaskTable/components/StatusLabel";
import {TASK_TYPES} from "mgmt/TaskTable/constants";
import PropTypes from "prop-types";
import React, {Component} from "react";

class TaskLabel extends Component {
    render() {
        const {id, due_date, status, type} = this.props.task;
        return (
            <div>
                <StatusLabel task={this.props.task} />
                <b>Task:</b>
                <span id={`type-${id}-task`}> {TASK_TYPES[type]}</span>
                <br />
                <DueDateLabel status={status} due_date={due_date} />
            </div>
        );
    }
}

TaskLabel.propTypes = {
    task: PropTypes.shape({
        id: PropTypes.number.isRequired,
        status: PropTypes.number.isRequired,
        status_display: PropTypes.string.isRequired,
        type: PropTypes.number.isRequired,
        due_date: PropTypes.object,
    }).isRequired,
};

export default TaskLabel;
