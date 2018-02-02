import React, { Component } from 'react';
import { connect } from 'react-redux';
import $ from '$';
import Study from 'study/Study';
import { fetchFullStudyIfNeeded } from 'robTable/actions';

class Header extends Component {

    render() {
        let headerText, smallText, heroID,
            { isForm, display } = this.props.config;
            console.log("hello");
            console.log(this.props.config.study.id);
            this.props.dispatch(fetchFullStudyIfNeeded());
            console.log(this.props.config.study);
        if(isForm){
            headerText = `${display == 'final' ? 'Final ' : ''}Review edit`;
            smallText = 'Justification for risk of bias assessment of selected study. Each row contains the selected domain, a description of the question to be answered, and an area for the user to detail the bias selection and notes for justification.';
            heroID = 12345;
            
        } else if(display == 'all'){
            headerText = 'Show all active reviews';
        }
        return (
            <div>
                <h3>
                    {headerText}
                </h3>
                <span className='help-text'>{smallText}</span>
                <p><a className='btn btn-mini btn-primary' target='_blank' href={'https://hero.epa.gov/hero/index.cfm/reference/downloads/reference_id/' + heroID}>Full text link <i className='fa fa-fw fa-file-pdf-o'></i></a><span>&nbsp;</span></p>
            </div>
        );
    }
}

function mapStateToProps(state){
    return {
        config: state.config,
    };
}

export default connect(mapStateToProps)(Header);
