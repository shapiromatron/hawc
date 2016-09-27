import React, { Component } from 'react';
import { connect } from 'react-redux';
import _ from 'underscore';

import { fetchTasks, fetchStudies, filterAndSortStudies, submitTasks } from 'mgmt/TaskTable/actions';

import { TASK_TYPES } from 'mgmt/TaskTable/constants';
import EmptyListNotification from 'shared/components/EmptyListNotification';
import Header from 'mgmt/TaskTable/components/Header';
import List from 'mgmt/TaskTable/components/List';
import Loading from 'shared/components/Loading';
import ScrollToErrorBox from 'shared/components/ScrollToErrorBox';
import SubmitButton from 'mgmt/TaskTable/components/SubmitButton';
import StudyFilter from 'mgmt/TaskTable/components/StudyFilter';
import TaskStudyEdit from 'mgmt/TaskTable/components/TaskStudyEdit';
import './Edit.css';


class EditApp extends Component {

    constructor(props) {
        super(props);
        this.filterStudies = this.filterStudies.bind(this);
        this.getTaskTypes = this.getTaskTypes.bind(this);
        this.updateForm = this.updateForm.bind(this);
    }


    componentWillMount() {
        this.props.dispatch(fetchTasks());
        this.props.dispatch(fetchStudies());
    }

    filterStudies(opts) {
        this.props.dispatch(filterAndSortStudies(opts));
    }

    formatTasks() {
        const { tasks, studies } = this.props,
            taskList = studies.visibleList.map((study) => {
                let formattedTasks = tasks.list.filter((task) => {
                    return task.study.id === study.id;
                }).sort((a, b) => (a.type - b.type));

                return {tasks: formattedTasks , study};
            });
        return taskList;
    }

    getTaskTypes() {
        const { tasks, studies } = this.props;
        return _.pluck(
                tasks.list.filter((task) => (
                    task.study.id === studies.list[0].id
                )).sort((a, b) => (a.type - b.type)),
                'type');
    }

    updateForm(e) {
        e.preventDefault();
        const updatedData = _.chain(this.refs.list.refs)
                    .map((ref) => { return ref.getChangedData(); })
                    .filter((data) => { return !_.isEmpty(data); })
                    .flatten()
                    .value();
        this.props.dispatch(submitTasks(updatedData));
    }

    render() {
        if (!this.props.tasks.isLoaded) return <Loading />;
        const { error } = this.props,
            taskList = this.formatTasks(),
            emptyTaskList = (taskList.length === 0),
            headings = emptyTaskList ? [] : this.getTaskTypes().map((type) => TASK_TYPES[type]);
        return (
                <div>
                    <ScrollToErrorBox error={error} />
                    <StudyFilter taskOptions={this.getTaskTypes()} selectFilter={this.filterStudies}/>
                    <Header headings={headings}/>
                    {emptyTaskList ? <EmptyListNotification listItem={'studies'} /> : <List component={TaskStudyEdit} items={taskList} ref='list' />}
                    <SubmitButton submitForm={this.updateForm} />
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

export default connect(mapStateToProps)(EditApp);
