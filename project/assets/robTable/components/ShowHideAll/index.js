import React, { Component, PropTypes } from 'react';

import './ShowHideAll.css';


class ShowHideAll extends Component {
    render() {
        let { actionText, handleClick } = this.props;
        return (
            <button className='btn btn-small' onClick={handleClick}>
                <i className='fa fa-plus'></i>
                {actionText} all details
            </button>
        );
    }
}

ShowHideAll.propTypes = {
    actionText: PropTypes.string.isRequired,
    handleClick: PropTypes.func.isRequired,
};

export default ShowHideAll;
