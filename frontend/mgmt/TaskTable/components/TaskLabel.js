import "./TaskLabel.css";

import DueDateLabel from "mgmt/TaskTable/components/DueDateLabel";
import StatusLabel from "mgmt/TaskTable/components/StatusLabel";
import PropTypes from "prop-types";
import React, {Component} from "react";

class TaskLabel extends Component {
    renderOwner(task) {
        if (!task.owner) {
            return null;
        }
        return (
            <div>
                <b>Owner: </b>
                {task.owner.full_name}
            </div>
        );
    }

    render() {
        const {task} = this.props;
        return (
            <div className="taskLabel">
                <StatusLabel task={task} />
                {this.renderOwner(task)}
                <DueDateLabel status={task.status} due_date={task.due_date} />
            </div>
        );
    }
}

TaskLabel.propTypes = {
    task: PropTypes.shape({
        owner: PropTypes.object,
        status: PropTypes.number.isRequired,
        status_display: PropTypes.string.isRequired,
        due_date: PropTypes.string,
    }).isRequired,
};

export default TaskLabel;
