import React, {Component} from "react";
import PropTypes from "prop-types";
import moment from "moment";
import DatePicker from "react-datepicker";

import "../../node_modules/react-datepicker/dist/react-datepicker.css";

class ReactDatePicker extends Component {
    constructor(props) {
        super(props);
        this.getDatePickerProps = this.getDatePickerProps.bind(this);
        this.onChange = this.onChange.bind(this);
        this.state = {
            date: props.date ? moment(props.date) : null,
        };
    }

    getDatePickerProps() {
        /*
            Only set selected as prop if state.date is set. If no date is passed
            to selected, then 'Invalid Date' is shown in input
        */
        let props = {
            id: this.props.id,
            className: "form-control",
            onChange: this.onChange,
        };
        if (this.state.date) props.selected = this.state.date;
        return props;
    }

    onChange(date, event) {
        this.setState({
            date,
        });
        this.props.onChange(date);
    }

    render() {
        const compProps = this.getDatePickerProps();
        return (
            <div className="form-group">
                <label htmlFor={compProps.id} className={this.props.labelClassName || ""}>
                    {this.props.label}
                </label>
                <DatePicker {...compProps} />
            </div>
        );
    }
}

ReactDatePicker.propTypes = {
    date: PropTypes.string,
    id: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    labelClassName: PropTypes.string,
    label: PropTypes.string,
};

export default ReactDatePicker;
