import React, {Component} from "react";
import PropTypes from "prop-types";
import {connect} from "react-redux";
import _ from "lodash";

import {fetchTasks, fetchStudies, filterAndSortStudies, submitTasks} from "mgmt/TaskTable/actions";

import {TASK_TYPES, TASK_TYPE_DESCRIPTIONS} from "mgmt/TaskTable/constants";
import CancelButton from "mgmt/TaskTable/components/CancelButton";
import EmptyListNotification from "shared/components/EmptyListNotification";
import Header from "mgmt/TaskTable/components/Header";
import List from "mgmt/TaskTable/components/List";
import Loading from "shared/components/Loading";
import ScrollToErrorBox from "shared/components/ScrollToErrorBox";
import SubmitButton from "mgmt/TaskTable/components/SubmitButton";
import StudyFilter from "mgmt/TaskTable/components/StudyFilter";
import TaskStudy from "mgmt/TaskTable/components/TaskStudy";
import TaskStudyEdit from "mgmt/TaskTable/components/TaskStudyEdit";
import "./List.css";

class ListApp extends Component {
    constructor(props) {
        super(props);
        this.handleCancel = this.handleCancel.bind(this);
        this.filterStudies = this.filterStudies.bind(this);
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
        const {tasks, studies} = this.props,
            taskList = studies.visibleList.map(study => {
                let formattedTasks = tasks.list
                    .filter(task => {
                        return task.study.id === study.id;
                    })
                    .sort((a, b) => a.type - b.type);

                return {tasks: formattedTasks, study};
            });
        return taskList;
    }

    handleCancel() {
        window.location.href = this.props.config.cancelUrl;
    }

    updateForm(e) {
        e.preventDefault();
        const updatedData = _.chain(this.refs.list.refs)
            .map(ref => {
                return ref.getChangedData();
            })
            .filter(data => {
                return !_.isEmpty(data);
            })
            .flattenDeep()
            .value();
        this.props.dispatch(submitTasks(updatedData));
    }

    render() {
        if (!this.props.tasks.isLoaded) return <Loading />;
        const {error, config} = this.props,
            taskList = this.formatTasks(),
            emptyTaskList = taskList.length === 0,
            headings = _.values(TASK_TYPES),
            descriptions = _.values(TASK_TYPE_DESCRIPTIONS),
            displayForm = config.type === "edit";

        return (
            <div>
                <ScrollToErrorBox error={error} />
                <StudyFilter selectFilter={this.filterStudies} />
                <Header headings={headings} descriptions={descriptions} />
                {emptyTaskList ? (
                    <EmptyListNotification listItem={"studies"} />
                ) : (
                    <List
                        component={displayForm ? TaskStudyEdit : TaskStudy}
                        items={taskList}
                        autocompleteUrl={this.props.config.autocomplete.url}
                        ref="list"
                    />
                )}
                {displayForm ? <SubmitButton submitForm={this.updateForm} /> : null}
                {displayForm ? <CancelButton onCancel={this.handleCancel} /> : null}
            </div>
        );
    }
}

function mapStateToProps(state) {
    const {error, tasks, studies, config} = state;
    return {
        config,
        error,
        tasks,
        studies,
    };
}

ListApp.propTypes = {
    dispatch: PropTypes.object,
    tasks: PropTypes.shape({
        list: PropTypes.object,
        isLoaded: PropTypes.object,
    }),
    studies: PropTypes.shape({
        visibleList: PropTypes.shape({
            map: PropTypes.object,
        }),
    }),
    config: PropTypes.shape({
        cancelUrl: PropTypes.object,
        type: PropTypes.object,
        autocomplete: PropTypes.object,
    }),
    error: PropTypes.object,
};

export default connect(mapStateToProps)(ListApp);
