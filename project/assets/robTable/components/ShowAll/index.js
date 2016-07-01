import React, { Component, PropTypes } from 'react';


class ShowAll extends Component {
    render() {
        let { handleClick } = this.props,
            text = (this.props.allShown)?
                'Hide all details':
                'Show all details',
            icons = (this.props.allShown)?
                'fa fa-minus fa-fw':
                'fa fa-plus fa-fw';

        return (
            <button className='btn btn-small' onClick={handleClick}>
                <i className={icons}></i>
                {text}
            </button>
        );
    }
}

ShowAll.propTypes = {
    allShown: PropTypes.bool.isRequired,
    handleClick: PropTypes.func.isRequired,
};

export default ShowAll;
