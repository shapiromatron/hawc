import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import '../../css/Assessment.css';

import Assessment from '../components/Assessment';
import Loading from '../components/Loading';

import { makeAssessmentActive } from '../actions/Assessment';

class App extends Component {

    componentWillMount() {
        const { id, dispatch } = this.props;
        dispatch(makeAssessmentActive(id));
    }

    render() {
        return <div>{this.props.children}</div>;
    }
}

function mapStateToProps(state){
    return {
        id: state.config.assessment_id,
    };
}

export default connect(mapStateToProps)(App);
