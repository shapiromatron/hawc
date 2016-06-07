import React, { Component } from 'react';
import { connect } from 'react-redux';


class Header extends Component {

    render() {
        let headerText, smallText;
        if(this.props.isForm){
            headerText = 'Final review edit';
            smallText = 'Justification for risk of bias assessment of selected study. Each row contains the selected domain, a description of the question to be answered, and an area for the user to detail the bias selection and notes for justification.';
        } else {
            headerText = 'Show all active reviews';
            smallText = null;
        }
        return (
            <div>
                <h3>
                    {headerText}
                </h3>
                <span className='help-text'>{smallText}</span>
            </div>
        );
    }
}

function mapStateToProps(state){
    return {
        isForm: state.config.isForm,
    };
}

export default connect(mapStateToProps)(Header);
