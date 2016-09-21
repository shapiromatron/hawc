import React, { Component, PropTypes } from 'react';

import TaskLabel from 'mgmt/TaskTable/components/TaskLabel';
import UpdateForm from 'mgmt/TaskTable/components/UpdateForm';


class TaskForm extends Component {

    constructor(props) {
        super(props);
        this.state = { showForm: false };
        this._toggleForm = this._toggleForm.bind(this);
        this._update = this._update.bind(this);
    }

    _toggleForm() {
        if (this.state.showForm) {
            this.setState({showForm: false});
        } else {
            this.setState({ showForm: true });
        }
    }

    _update() {
        this.props.task.update(this.props.task);
    }

    render() {
        const { task, className } = this.props;
        return (
            <div id={task.id} className={className}>
                <div onClick={this._toggleForm}>
                    <TaskLabel key={task.id} task={task} className={className}/>
                </div>
                {this.state.showForm ? <UpdateForm task={task} /> : null}
            </div>
        );
    }
}

TaskForm.propTypes = {
    className: PropTypes.string,
    task: PropTypes.shape({
        id: PropTypes.number.isRequired,
        owner: PropTypes.string,
        status: PropTypes.number.isRequired,
        status_display: PropTypes.string.isRequired,
    }).isRequired,
};

export default TaskForm;
