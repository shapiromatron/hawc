import "./Root.css";

import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Loading from "shared/components/Loading";
import ScrollToErrorBox from "shared/components/ScrollToErrorBox";

import StudyFilter from "./StudyFilter";
import TaskTable from "./TaskTable";

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
            noTasks = taskList.length === 0;

        return (
            <div>
                <ScrollToErrorBox error={store.error} />
                <StudyFilter selectFilter={opts => store.filterAndSortStudies(opts)} />
                {noTasks ? <h4>No studies match the given query.</h4> : <TaskTable />}
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
