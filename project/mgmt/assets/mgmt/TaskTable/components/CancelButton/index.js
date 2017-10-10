import React, { Component, PropTypes } from 'react';


class CancelButton extends Component {
    render() {
        return (
            <button onClick={this.props.onCancel} className='btn space'>Cancel</button>
        );
    }
}

CancelButton.propTypes = {
    onCancel: PropTypes.func.isRequired,
};

export default CancelButton;
