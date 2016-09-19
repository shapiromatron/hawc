import React, { Component } from 'react';
import { connect } from 'react-redux';
import _ from 'underscore';

import { fetchTasks } from 'mgmt/TaskTable/actions';
import { fetchStudies } from 'mgmt/TaskTable/actions';

import { TASK_TYPES } from 'mgmt/TaskTable/constants';
import Header from 'mgmt/TaskTable/components/Header';
import List from 'mgmt/TaskTable/components/List';
import Loading from 'shared/components/Loading';
import ScrollToErrorBox from 'shared/components/ScrollToErrorBox';
import TaskStudy from 'mgmt/TaskTable/components/TaskStudy';


class App extends Component {

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
            headings = _.pluck(taskList[0].tasks, 'type').map((type) => TASK_TYPES[type]);
        return (
                <div>
                    <ScrollToErrorBox error={error} />
                    <Header headings={headings}/>
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

export default connect(mapStateToProps)(App);
