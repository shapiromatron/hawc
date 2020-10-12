import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";

import {inject, observer} from "mobx-react";

import GenericError from "shared/components/GenericError";
import Loading from "shared/components/Loading";
import TaskChart from "../components/TaskChart";
import {STATUS} from "../constants";

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        this.props.store.fetchTasks();
    }

    getChartData() {
        const height = 200,
            width = 500,
            padding = {top: 20, right: 0, bottom: 50, left: 75},
            yTransform = [padding.left, 0],
            xTransform = [0, height - padding.bottom],
            colors = {};
        Object.keys(STATUS).map(key => (colors[key] = STATUS[key].color));
        return {height, width, padding, yTransform, xTransform, colors};
    }

    renderTasksByType(chartData, list) {
        let types = _.chain(list)
            .map("type")
            .uniq()
            .value();

        return types.map(function(type) {
            let subset = list.filter(d => d.type === type),
                data = _.extend({}, chartData, {
                    label: subset[0].type_display,
                });
            return (
                <div key={`type-${type}`}>
                    <TaskChart chartData={data} tasks={subset} />
                </div>
            );
        });
    }

    renderTasksByUser(chartData, list) {
        let users = _.chain(list)
            .map(d => (d.owner ? d.owner.full_name : null))
            .compact()
            .uniq()
            .value();

        return users.map(function(user) {
            let subset = list.filter(d => d.owner && d.owner.full_name === user),
                data = _.extend({}, chartData, {
                    label: subset[0].owner.full_name,
                });
            return (
                <div key={`user-${user}`}>
                    <TaskChart chartData={data} tasks={subset} />
                </div>
            );
        });
    }

    render() {
        const {store} = this.props;

        if (store.error) {
            return <GenericError />;
        }

        if (store.isFetching) {
            return <Loading />;
        }

        if (store.tasks === null || store.tasks.length === 0) {
            return <p>To tasks have yet assigned.</p>;
        }

        let chartData = this.getChartData();
        return (
            <div>
                <h3>All task summary</h3>
                <TaskChart chartData={chartData} tasks={store.tasks} />
                <h3>Tasks by type</h3>
                {this.renderTasksByType(chartData, store.tasks)}
                <h3>Tasks by user</h3>
                {this.renderTasksByUser(chartData, store.tasks)}
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
