import React, { Component } from 'react';
import { connect } from 'react-redux';
import _ from 'underscore';

import { fetchTasks } from 'mgmt/TaskTable/actions';
import { fetchStudies } from 'mgmt/TaskTable/actions';

import {
    TASK_TYPES,
    TASK_TYPE_DESCRIPTIONS,
} from 'mgmt/TaskTable/constants';
import Header from 'mgmt/TaskTable/components/Header';
import List from 'mgmt/TaskTable/components/List';
import Loading from 'shared/components/Loading';
import ScrollToErrorBox from 'shared/components/ScrollToErrorBox';
import TaskStudy from 'mgmt/TaskTable/components/TaskStudy';


class ListApp extends Component {

    componentWillMount() {
        this.props.dispatch(fetchTasks());
        this.props.dispatch(fetchStudies());
    }

    _formatTasks() {
        const { tasks, studies } = this.props,
            taskList = studies.list.map((study) => {
                let formattedTasks = tasks.list.filter((task) => {
                    return task.study.id === study.id;
                }).sort((a, b) => (a.type - b.type));

                return {tasks: formattedTasks , study};
            });
        return taskList;
    }

    render() {
        if (!this.props.tasks.isLoaded) return <Loading />;
        const { error } = this.props,
            taskList = this._formatTasks(),
            headings = _.values(TASK_TYPES),
            descriptions = _.values(TASK_TYPE_DESCRIPTIONS);

        return (
                <div>
                    <ScrollToErrorBox error={error} />
                    <Header headings={headings} descriptions={descriptions}/>
                    <List component={TaskStudy} items={taskList} />
                </div>
        );
    }
}

function mapStateToProps(state){
    const { error, tasks, studies } = state;
    return {
        error,
        tasks,
        studies,
    };
}

export default connect(mapStateToProps)(ListApp);
