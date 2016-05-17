import React, { Component } from 'react';
import { connect } from 'react-redux';


class Header extends Component {

    render() {
        return (
            <h2>
                {this.props.form ? 'Final review edit' : 'Show all active reviews'}
            </h2>
        );
    }
}

function mapStateToProps(state){
    return {
        form: state.config.form,
    };
}

export default connect(mapStateToProps)(Header);
