import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';

import Assessment from '../components/Assessment';
import Loading from '../components/Loading';

import { fetchObjectIfNeeded } from '../actions/Assessment';

class App extends Component {

    componentWillMount() {
        const { id } = this.props;
        this.props.dispatch(fetchObjectIfNeeded(id));
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
