import React, { Component, PropTypes } from 'react';

import DueDateLabel from 'mgmt/TaskTable/components/DueDateLabel';
import StatusIcon from 'mgmt/TaskTable/components/StatusIcon';
import './TaskLabel.css';


class TaskLabel extends Component {

    render() {
        const { task, className } = this.props;
        return (
            <div className={`taskLabel ${className}`}>
                <div>Status: <StatusIcon status={task.status} /> {task.status_display}</div>
                <div>Owner: {task.owner ? task.owner.full_name : '-'}</div>
                <DueDateLabel due_date={task.due_date} />
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
