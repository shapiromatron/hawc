import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import Loading from "shared/components/Loading";
import EmptyListNotification from "shared/components/EmptyListNotification";
import ScrollToErrorBox from "shared/components/ScrollToErrorBox";

import {TASK_TYPES, TASK_TYPE_DESCRIPTIONS} from "../constants";
import Header from "../components/Header";
import List from "../components/List";
import StudyFilter from "../components/StudyFilter";
import TaskStudy from "../components/TaskStudy";
import TaskStudyEdit from "../components/TaskStudyEdit";

import "./Root.css";

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        const {store} = this.props;
        store.fetchTasks();
        store.fetchStudies();
    }

    render() {
        if (!this.props.store.isReady) {
            return <Loading />;
        }

        const {store} = this.props,
            taskList = store.taskListByStudy,
            emptyTaskList = taskList.length === 0,
            headings = _.values(TASK_TYPES),
            descriptions = _.values(TASK_TYPE_DESCRIPTIONS),
            displayForm = store.config.type === "edit";

        return (
            <div>
                <ScrollToErrorBox error={store.error} />
                <StudyFilter selectFilter={opts => store.filterAndSortStudies(opts)} />
                <Header headings={headings} descriptions={descriptions} />
                {emptyTaskList ? (
                    <EmptyListNotification listItem={"studies"} />
                ) : (
                    <List
                        component={displayForm ? TaskStudyEdit : TaskStudy}
                        items={taskList}
                        autocompleteUrl={store.config.autocomplete.url}
                        ref={c => (this.list = c)}
                    />
                )}
                {displayForm ? (
                    <>
                        <button
                            onClick={event => {
                                event.preventDefault();
                                const updatedData = _.chain(this.list.components)
                                    .filter(component => component != null)
                                    .map(component => component.getChangedData())
                                    .filter(data => !_.isEmpty(data))
                                    .flattenDeep()
                                    .value();
                                store.submitTasks(updatedData);
                            }}
                            className="btn btn-primary">
                            Submit changes
                        </button>
                        <button
                            onClick={() => {
                                const {cancelUrl} = this.props.store.config;
                                window.location.href = cancelUrl;
                            }}
                            className="btn space">
                            Cancel
                        </button>
                    </>
                ) : null}
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
