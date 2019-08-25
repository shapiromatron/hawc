import React, { Component } from 'react';
import { connect } from 'react-redux';

class Header extends Component {
    render() {
        let headerText,
            { isForm, display } = this.props.config;
        if (isForm) {
            headerText = display == 'final' ? 'Final review' : 'Review';
        } else if (display == 'all') {
            headerText = 'Show all active reviews';
        }
        return (
            <div>
                <h3>{headerText}</h3>
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        config: state.config,
    };
}

export default connect(mapStateToProps)(Header);
