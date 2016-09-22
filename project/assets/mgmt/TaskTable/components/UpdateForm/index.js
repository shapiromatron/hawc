import React, { Component, PropTypes } from 'react';

import UserAutocomplete from 'mgmt/TaskTable/components/UserAutocomplete';
import StatusSelection from 'mgmt/TaskTable/components/StatusSelection';
import DueDateSelection from 'mgmt/TaskTable/components/DueDateSelection';


class UpdateForm extends Component {
    render() {
        const { task } = this.props;
        return (
            <div>
                <UserAutocomplete task={task} />
                <StatusSelection task={task} />
                <DueDateSelection task={task} />
            </div>
        );
    }
}

UpdateForm.propTypes = {
    task: PropTypes.shape({
        due_date: PropTypes.string.isRequired,
        id: PropTypes.number.isRequired,
        study: PropTypes.shape({
            assessment: PropTypes.number.isRequired,
        }).isRequired,
        status: PropTypes.number.isRequired,
    }).isRequired,
};

export default UpdateForm;
