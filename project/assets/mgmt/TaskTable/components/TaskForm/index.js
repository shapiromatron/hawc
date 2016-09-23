import React, { Component, PropTypes } from 'react';

import UserAutocomplete from 'mgmt/TaskTable/components/UserAutocomplete';
import StatusSelection from 'mgmt/TaskTable/components/StatusSelection';
import DueDateSelection from 'mgmt/TaskTable/components/DueDateSelection';


class TaskForm extends Component {

    constructor(props) {
        super(props);
        const { owner, status, due_date } = props.task;
        this.state = {
            owner,
            status,
            due_date,
        };

        this.getOwnerUpdate = this.getOwnerUpdate.bind(this);
        this.getStatusUpdate = this.getStatusUpdate.bind(this);
        this.getDueDateUpdate = this.getDueDateUpdate.bind(this);
    }


    getOwnerUpdate() {

    }

    getStatusUpdate() {

    }

    getDueDateUpdate() {

    }

    render() {
        const { task, className } = this.props;
        return (
            <div className={className}>
                <UserAutocomplete onChange={this.getOwnerUpdate} task={task} />
                <StatusSelection onChange={this.getStatusUpdate} task={task} />
                <DueDateSelection onChange={this.getDueDateUpdate} task={task} />
            </div>
        );
    }
}

TaskForm.propTypes = {
    task: PropTypes.shape({
        due_date: PropTypes.string,
        id: PropTypes.number.isRequired,
        study: PropTypes.shape({
            assessment: PropTypes.number.isRequired,
        }).isRequired,
        status: PropTypes.number.isRequired,
    }).isRequired,
    className: PropTypes.string.isRequired,
};

export default TaskForm;
