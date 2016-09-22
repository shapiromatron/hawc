import React, { Component, PropTypes } from 'react';

import { STATUS } from 'mgmt/TaskTable/constants';


class StatusSelection extends Component {

    getStatusChoices() {
        return Object.keys(STATUS).map((status) => {
            return {value: status, display: STATUS[status].type };
        });
    }

    render() {
        const choices = this.getStatusChoices(),
            idName = `${this.props.task.id}-status_selection`;
        return (
            <div>
                <label htmlFor={idName}>Status</label>
                <select name="status_selection" id={idName} style={{width: 'auto'}}>
                    {choices.map(({value, display }, i) => {
                        return <option key={i} value={value}>{display}</option>;
                    })}
                </select>
            </div>
        );
    }
}

StatusSelection.propTypes = {
    task: PropTypes.shape({
        id: PropTypes.number.isRequired,
    }).isRequired,
};

export default StatusSelection;
