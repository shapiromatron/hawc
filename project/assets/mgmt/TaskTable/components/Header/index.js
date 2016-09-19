import React, { Component, PropTypes } from 'react';


class Header extends Component {
    render() {
        return (
            <div className='flexRow-container'>
                <h5 className='flex-1'>Study</h5>
                {this.props.headings.map((heading, i) => {
                    return <h5 key={`heading-${i}`} className='flex-1'>{heading}</h5>;
                })}
            </div>
        );
    }
}

Header.propTypes = {
    headings: PropTypes.arrayOf(
        PropTypes.string
    ).isRequired,
};

export default Header;
