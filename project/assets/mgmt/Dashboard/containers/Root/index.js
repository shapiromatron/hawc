import React, { Component } from 'react';
import { connect } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import { fetchTasks } from 'mgmt/Dashboard/actions';
import TaskChart from 'mgmt/Dashboard/components/TaskChart';
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
                <TaskChart tasks={this.props.tasks} />
                <UnderConstruction />
            </div>
        );
    }
}

function mapStateToProps(state){
    return state;
}

export default connect(mapStateToProps)(Root);
