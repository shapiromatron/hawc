import _ from 'underscore';
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

    renderNoTasks(){
        return <p>To tasks have yet assigned.</p>;
    }

    renderTasksByType(chartData, list){
        let types = _.chain(list)
            .pluck('type')
            .uniq()
            .value();

        return types.map(function(type){
            let subset = list.filter((d) => d.type === type),
                data = _.extend({}, chartData, {
                    label: subset[0].type_display,
                });
            return <div key={`type-${type}`}>
                <TaskChart chartData={data} tasks={subset} />
            </div>;
        });
    }

    renderTasksByUser(chartData, list){
        let users = _.chain(list)
            .map((d)=> (d.owner)? d.owner.full_name: null)
            .compact()
            .uniq()
            .value();

        return users.map(function(user){
            let subset = list.filter((d) => d.owner && d.owner.full_name === user),
                data = _.extend({}, chartData, {
                    label: subset[0].owner.full_name,
                });
            return <div key={`user-${user}`}>
                <TaskChart chartData={data} tasks={subset} />
            </div>;
        });
    }

    render() {
        if (!this.props.tasks.isLoaded){
            return <Loading />;
        }

        if (this.props.tasks.list.length === 0){
            return this.renderNoTasks();
        }

        let list = this.props.tasks.list,
            chartData = this.getChartData();
        return (
            <div>
                <h3>All task summary</h3>
                <TaskChart chartData={chartData} tasks={list} />
                <h3>Tasks by type</h3>
                {this.renderTasksByType(chartData, list)}
                <h3>Tasks by user</h3>
                {this.renderTasksByUser(chartData, list)}
            </div>
        );
    }
}

function mapStateToProps(state){
    return state;
}

export default connect(mapStateToProps)(Root);
