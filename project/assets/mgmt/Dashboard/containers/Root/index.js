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
            padding = {top: 20, right: 70, bottom: 70, left: 55},
            yTransform = [padding.left, 0],
            xTransform = [0, height - padding.bottom];
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
