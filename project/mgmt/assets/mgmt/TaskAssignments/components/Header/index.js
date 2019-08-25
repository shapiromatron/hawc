import React, { Component } from 'react';
import PropTypes from 'prop-types';

class Header extends Component {
    render() {
        return (
            <div className="flexRow-container">
                {this.props.headings.map((heading, i) => {
                    return (
                        <h4 key={`heading-${i}`} className={`flex-${heading.flex}`}>
                            {heading.name}
                        </h4>
                    );
                })}
            </div>
        );
    }
}

Header.propTypes = {
    headings: PropTypes.array.isRequired,
};

export default Header;
