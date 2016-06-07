import React, { Component, PropTypes } from 'react';

import './ShowAll.css';


class ShowAll extends Component {
    render() {
        let { handleClick } = this.props;
        return (
            <button className='btn btn-small' onClick={handleClick}>
                <i className='fa fa-plus show-plus'></i>
                Show all details
            </button>
        );
    }
}

ShowAll.propTypes = {
    handleClick: PropTypes.func.isRequired,
};

export default ShowAll;
