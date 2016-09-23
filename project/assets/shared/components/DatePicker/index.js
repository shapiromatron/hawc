import React, { Component, PropTypes } from 'react';
import ReactDOM from 'react-dom';
import moment from 'moment';


class DatePicker extends Component {
    /*
        Renders a jQueryUI Datepicker.
        props.opts: {
            changeMonth: same as jQ,
            changeYear: same as jQ,
            showAnim: same as jQ,
            yearRange: same as jQ,
            onSelect: function to be called when date is selected. Returns date
                    in UTC format.
            setDate: string date to populate Datepicker with.
        }
    */

    constructor(props) {
        super(props);
        this.formatDatePickerOutput = this.formatDatePickerOutput.bind(this);
        this.formatDjangoDate = this.formatDjangoDate.bind(this);

        this.state = {
            opts: {...props.opts,
                onSelect: this.formatDatePickerOutput,
                setDate: this.formatDjangoDate(this.props.opts.setDate)
            },
        };
    }

    formatDatePickerOutput(date) {
        /* returns date in UTC format for submitting to Django */
        this.props.opts.onSelect(moment(date).utc().format());
    }

    formatDjangoDate(populatedDate) {
        return populatedDate ? new Date(populatedDate) : populatedDate;
    }

    componentDidMount() {
        $(ReactDOM.findDOMNode(this))
            .datepicker(this.state.opts)
            .datepicker('setDate', this.state.opts.setDate);
    }

    componentWillUnmount() {
        $(ReactDOM.findDOMNode(this)).datepicker('destroy');
    }

    render() {
        return (
                <input type='text' id={this.props.id} style={{width: 'auto'}} />
        );
    }
}

DatePicker.propTypes = {
    opts: PropTypes.shape({
        changeMonth: PropTypes.bool,
        changeYear: PropTypes.bool,
        onSelect: PropTypes.func.isRequired,
        setDate: PropTypes.string,
        showAnim: PropTypes.string,
        yearRange: PropTypes.string,
    }).isRequired,
    id: PropTypes.string.isRequired,
};

export default DatePicker;
