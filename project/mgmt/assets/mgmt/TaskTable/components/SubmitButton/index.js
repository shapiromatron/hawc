import React, { Component, PropTypes } from 'react';


class SubmitButton extends Component {
    render() {
        return (
            <button onClick={this.props.submitForm} className='btn btn-primary'>Submit changes</button>
        );
    }
}

SubmitButton.propTypes = {
    submitForm: PropTypes.func.isRequired,
};

export default SubmitButton;
