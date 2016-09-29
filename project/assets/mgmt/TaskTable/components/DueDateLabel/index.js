import React, { Component, PropTypes } from 'react';
import moment from 'moment';


class DueDateLabel extends Component {
    render() {
        const { due_date, status } = this.props,
            pastDueStyle = status < 30 ?
                            moment().isAfter(due_date) ? {backgroundColor: 'yellow', maxWidth: '175px'} : null
                            : null,
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
    status: PropTypes.number.isRequired,
};

export default DueDateLabel;
