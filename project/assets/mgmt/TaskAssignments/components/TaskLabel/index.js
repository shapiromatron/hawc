import React, { Component, PropTypes } from 'react';

import h from 'mgmt/utils/helpers';
import DueDateLabel from 'mgmt/TaskTable/components/DueDateLabel';
import StatusIcon from 'mgmt/TaskTable/components/StatusIcon';
import { TASK_TYPES } from 'mgmt/TaskTable/constants';


class TaskLabel extends Component {
    render() {
        const { id, due_date, status, status_display, type } = this.props.task;
        return (
            <div className={this.props.className}>
                <label htmlFor={`type-${id}-task`} style={{cursor: 'default'}}>Task:
                    <span id={`type-${id}-task`}> {TASK_TYPES[type]}</span>
                </label>
                <label htmlFor={`type-${id}-status`} style={{cursor: 'default'}}>Status:
                    <span id={`type-${id}-status`}> <StatusIcon status={status} /> {h.caseToWords(status_display)}</span>
                </label>
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
    }).isRequired,
};

export default TaskLabel;
