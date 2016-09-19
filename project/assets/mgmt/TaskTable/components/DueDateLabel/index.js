import React, { Component, PropTypes } from 'react';
import moment from 'moment';


class DueDateLabel extends Component {
    render() {
        const { due_date } = this.props,
            pastDueStyle = moment().isAfter(due_date) ? {backgroundColor: 'yellow', maxWidth: '175px'} : null,
            dueDate = due_date ? moment(due_date).format('MM/DD/YYYY') : '-';
        return (
            <div style={pastDueStyle}>
                Due date: {dueDate}
            </div>
        );
    }
}

DueDateLabel.propTypes = {
    due_date: PropTypes.string,
};

export default DueDateLabel;
