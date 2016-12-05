import React, { Component } from 'react';
import { connect } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import { fetchTasks } from 'mgmt/Dashboard/actions';
import Loading from 'shared/components/Loading';
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

    getChartData() {
        const height = 200,
            width = 500,
            padding = [20, 70, 70, 55],
            yTransform = [padding[3], 0],
            xTransform = [0, height - padding[2]];
        return {height, width, padding, yTransform, xTransform};
    }

    render() {
        return (
            this.props.tasks.isLoaded ?
            <div>
                <TaskChart chartData={this.getChartData()} tasks={this.props.tasks.list} />
                <UnderConstruction />
            </div> :
            <Loading />
        );
    }
}

function mapStateToProps(state){
    return state;
}

export default connect(mapStateToProps)(Root);
