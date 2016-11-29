import React, { Component } from 'react';
import { connect } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import { fetchTasks } from 'mgmt/Dashboard/actions';
import UnderConstruction from 'mgmt/Dashboard/components/UnderConstruction';

class Root extends Component {

    constructor(props) {
        super(props);
        props.dispatch(loadConfig());
    }

    componentWillMount() {
        this.props.dispatch(fetchTasks());
    }

    render() {
        return (
            <div>
                <UnderConstruction />
            </div>
        );
    }
}

function mapStateToProps(state){
    return state;
}

export default connect(mapStateToProps)(Root);
