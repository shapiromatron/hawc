import React, { Component, PropTypes } from 'react';

import DatePicker from 'shared/components/DatePicker';


class DueDateSelection extends Component {

    constructor(props) {
        super(props);
        this.getOptions = this.getOptions.bind(this);
    }

    getOptions() {
        let opts = {
            showAnim: 'slideDown',
            changeMonth: true,
            changeYear: true,
            yearRange: '1930 : * ',
        };
        if (this.props.task.due_date){
            opts = {...opts, setDate: this.props.task.due_date};
        }
        return opts;
    }

    render() {
        let idName = `${this.props.task.id}-due_date`;
        return (
            <div>
                <label htmlFor={idName}>Due Date</label><DatePicker opts={this.getOptions()} id={idName} />
            </div>
        );
    }
}

DueDateSelection.propTypes = {
    task: PropTypes.shape({
        due_date: PropTypes.string,
        id: PropTypes.number.isRequired,
    }).isRequired,
};

export default DueDateSelection;
