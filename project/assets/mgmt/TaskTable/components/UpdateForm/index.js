import React, { Component, PropTypes } from 'react';

import UserAutocomplete from 'mgmt/TaskTable/components/UserAutocomplete';


class UpdateForm extends Component {
    render() {
        return (
            <div>
                <UserAutocomplete task={this.props.task} />
            </div>
        );
    }
}

UpdateForm.propTypes = {
};

export default UpdateForm;
