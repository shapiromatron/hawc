import React, { Component } from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';

import UserAutocomplete from 'mgmt/TaskTable/components/UserAutocomplete';
import StatusSelection from 'mgmt/TaskTable/components/StatusSelection';
import ReactDatePicker from 'shared/components/ReactDatePicker';

class TaskForm extends Component {
    constructor(props) {
        super(props);
        const { owner, status, due_date, id } = props.task;
        this.state = {
            id,
            owner,
            status,
            due_date,
        };

        this.formDidChange = this.formDidChange.bind(this);
        this.getOwnerUpdate = this.getOwnerUpdate.bind(this);
        this.getStatusUpdate = this.getStatusUpdate.bind(this);
        this.getDueDateUpdate = this.getDueDateUpdate.bind(this);
    }

    formDidChange() {
        const { owner, status, due_date, id } = this.props.task;
        return !_.isEqual(this.state, { owner, status, due_date, id });
    }

    getOwnerUpdate(owner) {
        this.setState({
            owner: {
                id: owner.id,
                full_name: owner.value,
            },
        });
    }

    getStatusUpdate(status) {
        this.setState({
            status,
        });
    }

    getDueDateUpdate(due_date) {
        this.setState({
            due_date,
        });
    }

    render() {
        const { task, className, autocompleteUrl } = this.props;
        return (
            <div className={className}>
                <UserAutocomplete
                    onChange={this.getOwnerUpdate}
                    task={task}
                    url={autocompleteUrl}
                />
                <StatusSelection onChange={this.getStatusUpdate} task={task} />
                <ReactDatePicker
                    onChange={this.getDueDateUpdate}
                    labelClassName="control-label"
                    label="Due date (optional)"
                    id={`${task.id}-due_date`}
                    date={task.due_date}
                />
            </div>
        );
    }
}

TaskForm.propTypes = {
    task: PropTypes.shape({
        due_date: PropTypes.string,
        id: PropTypes.number.isRequired,
        status: PropTypes.number.isRequired,
        status_display: PropTypes.string.isRequired,
        study: PropTypes.shape({
            assessment: PropTypes.object.isRequired,
        }).isRequired,
    }).isRequired,
    className: PropTypes.string,
    autocompleteUrl: PropTypes.string.isRequired,
};

export default TaskForm;
