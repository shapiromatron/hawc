import React, { Component, PropTypes } from 'react';
import ReactDOM from 'react-dom';

class DatePicker extends Component {

    componentDidMount() {
        $(ReactDOM.findDOMNode(this)).datepicker(this.props.opts);
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
        showAnim: PropTypes.string,
        changeMonth: PropTypes.bool,
        changeYear: PropTypes.bool,
        yearRange: PropTypes.string,
        setDate: PropTypes.string,
    }).isRequired,
    id: PropTypes.string.isRequired,
};

export default DatePicker;
