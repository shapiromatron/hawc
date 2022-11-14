import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDatePicker from "shared/components/ReactDatePicker";

import StatusSelection from "./StatusSelection";
import UserAutocomplete from "./UserAutocomplete";

class TaskForm extends Component {
    constructor(props) {
        super(props);
        const {owner, status, due_date, id} = props.task;
        this.state = {
            id,
            owner,
            status,
            due_date,
        };
    }

    hasDataChanged() {
        const {owner, status, due_date, id} = this.props.task;
        return !_.isEqual(this.state, {owner, status, due_date, id});
    }

    componentDidUpdate() {
        if (this.props.onFormChange) {
            this.props.onFormChange(this.state);
        }
    }

    render() {
        const {task, className, autocompleteUrl} = this.props;
        return (
            <div className={className}>
                <UserAutocomplete
                    onChange={owner => {
                        const ownerObject = owner
                            ? {
                                  id: owner.id,
                                  full_name: owner.value,
                              }
                            : null;
                        this.setState({owner: ownerObject});
                    }}
                    task={task}
                    url={autocompleteUrl}
                />
                <StatusSelection
                    onChange={status => this.setState({status})}
                    defaultValue={task.status}
                />
                <ReactDatePicker
                    onChange={date => this.setState({due_date: date})}
                    labelClassName="col-form-label"
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
        owner: PropTypes.object,
    }).isRequired,
    className: PropTypes.string,
    autocompleteUrl: PropTypes.string.isRequired,
    onFormChange: PropTypes.func,
};

export default TaskForm;
