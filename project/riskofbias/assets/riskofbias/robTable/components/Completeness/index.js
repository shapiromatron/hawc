import React, { Component } from 'react';
import PropTypes from 'prop-types';


class Completeness extends Component {

    render() {
        let display = this.props.number.size ?
            <div className='alert alert-danger'>
                <p>{this.props.number.size} notes still need input.</p>
                <p>Notes should only be left blank if "Not applicable" score is selected.</p>
            </div> : null;
        return display;
    }
}

Completeness.propTypes = {
    number: PropTypes.object,
};

export default Completeness;
