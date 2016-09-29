import React, { Component } from 'react';
import { connect } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import Assignments from 'mgmt/TaskAssignments/components/Assignments';

class Root extends Component {

    componentWillMount() {
        this.props.dispatch(loadConfig());
    }

    render() {
        return (<Assignments {...this.props}/>);
    }
}

function mapStateToProps(state){
    return state;
}

export default connect(mapStateToProps)(Root);
