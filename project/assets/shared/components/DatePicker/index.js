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
