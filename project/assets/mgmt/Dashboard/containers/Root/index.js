import React, { Component } from 'react';
import { connect } from 'react-redux';

import { loadConfig } from 'shared/actions/Config';
import { fetchTasks } from 'mgmt/Dashboard/actions';
import Loading from 'shared/components/Loading';
import TaskChart from 'mgmt/Dashboard/components/TaskChart';
import { STATUS } from 'mgmt/Dashboard/constants';

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
            padding = {top: 20, right: 0, bottom: 50, left: 75},
            yTransform = [padding.left, 0],
            xTransform = [0, height - padding.bottom],
            colors = {};
        Object.keys(STATUS).map((key) => colors[key] = STATUS[key].color );
        return {height, width, padding, yTransform, xTransform, colors};
    }

    render() {
        return (
            this.props.tasks.isLoaded ?
            <div>
                <TaskChart chartData={this.getChartData()} tasks={this.props.tasks.list} />
            </div> :
            <Loading />
        );
    }
}

function mapStateToProps(state){
    return state;
}

export default connect(mapStateToProps)(Root);
