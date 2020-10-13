import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import Loading from "shared/components/Loading";
import EmptyListNotification from "shared/components/EmptyListNotification";
import ScrollToErrorBox from "shared/components/ScrollToErrorBox";

import {TASK_TYPES, TASK_TYPE_DESCRIPTIONS} from "../constants";
import Header from "./Header";
import List from "./List";
import StudyFilter from "./StudyFilter";
import TaskStudy from "./TaskStudy";
import TaskStudyEdit from "./TaskStudyEdit";

import "./Root.css";

@inject("store")
@observer
class Root extends Component {
    constructor(props) {
        super(props);
        this.handleCancel = this.handleCancel.bind(this);
        this.filterStudies = this.filterStudies.bind(this);
        this.updateForm = this.updateForm.bind(this);
    }

    componentDidMount() {
        const {store} = this.props;
        store.fetchTasks();
        store.fetchStudies();
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

    updateForm(e) {
        e.preventDefault();
        const updatedData = _.chain(this.list.components)
            .filter(component => component != null)
            .map(component => {
                return component.getChangedData();
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
                        ref={c => (this.list = c)}
                    />
                )}
                {displayForm ? (
                    <button onClick={this.updateForm} className="btn btn-primary">
                        Submit changes
                    </button>
                ) : null}
                {displayForm ? (
                    <button
                        onClick={() => {
                            const {store} = this.props;
                            window.location.href = store.config.cancelUrl;
                        }}
                        className="btn space">
                        Cancel
                    </button>
                ) : null}
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
