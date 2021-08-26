import _ from "lodash";
import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import GenericError from "shared/components/GenericError";
import Loading from "shared/components/Loading";

import TaskChart from "./TaskChart";

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        this.props.store.fetchTasks();
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

        const {tasks} = store,
            types = _.chain(tasks)
                .map("type")
                .uniq()
                .value(),
            users = _.chain(tasks)
                .map(d => (d.owner ? d.owner.full_name : null))
                .compact()
                .uniq()
                .value();

        return (
            <>
                <h3>All task summary</h3>
                <TaskChart tasks={tasks} label="" />
                <h3>Tasks by type</h3>
                {types.map(type => {
                    const data = tasks.filter(d => d.type === type),
                        label = data[0].type_display;
                    return <TaskChart key={`type-${type}`} tasks={data} label={label} />;
                })}
                <h3>Tasks by user</h3>
                {users.map(user => {
                    const data = tasks.filter(d => d.owner && d.owner.full_name === user),
                        label = data[0].owner.full_name;
                    return <TaskChart key={`user-${user}`} tasks={data} label={label} />;
                })}
            </>
        );
    }
}
Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
