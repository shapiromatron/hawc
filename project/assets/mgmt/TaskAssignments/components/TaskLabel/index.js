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
                <b>Task:</b><span id={`type-${id}-task`}> {TASK_TYPES[type]}</span><br/>
                <b>Status:</b><span id={`type-${id}-status`}><StatusIcon status={status}/>{h.caseToWords(status_display)}</span><br/>
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
