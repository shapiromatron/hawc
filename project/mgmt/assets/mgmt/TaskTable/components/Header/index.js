import $ from '$';
import React, { Component } from 'react';
import PropTypes from 'prop-types';


class Header extends Component {

    componentDidMount(){
        $('.popovers').popover({
            placement: 'top',
            trigger: 'hover',
        });
    }

    render() {
        let descriptions = this.props.descriptions;
        return (
            <div className='flexRow-container'>
                <h5 className='flex-1'>Study</h5>
                {this.props.headings.map((heading, i) => {
                    return <h5 key={`heading-${i}`} className='popovers flex-1' data-title={heading} data-content={descriptions[i]} >{heading}</h5>;
                })}
            </div>
        );
    }
}

Header.propTypes = {
    headings: PropTypes.arrayOf(
        PropTypes.string
    ).isRequired,
    descriptions: PropTypes.arrayOf(
        PropTypes.string
    ).isRequired,
};

export default Header;
