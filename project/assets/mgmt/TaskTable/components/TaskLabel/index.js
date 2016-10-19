import React, { Component, PropTypes } from 'react';

import DueDateLabel from 'mgmt/TaskTable/components/DueDateLabel';
import StatusIcon from 'mgmt/TaskTable/components/StatusIcon';
import './TaskLabel.css';


class TaskLabel extends Component {

    renderOwner(task){
        if (!task.owner){
            return null;
        }
        return <div><b>Owner: </b>{task.owner.full_name}</div>;
    }

    render() {
        const { task, className } = this.props;
        return (
            <div className={`taskLabel ${className}`}>
                <div><b>Status: </b><StatusIcon status={task.status} /> {task.status_display}</div>
                {this.renderOwner(task)}
                <DueDateLabel status={task.status} due_date={task.due_date} />
            </div>
        );
    }
}

TaskLabel.propTypes = {
    className: PropTypes.string.isRequired,
    task: PropTypes.shape({
        owner: PropTypes.object,
        status: PropTypes.number.isRequired,
        status_display: PropTypes.string.isRequired,
        due_date: PropTypes.string,
    }).isRequired,
};

export default TaskLabel;
