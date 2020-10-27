import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import Loading from "shared/components/Loading";
import ScrollToErrorBox from "shared/components/ScrollToErrorBox";

import TaskTable from "./TaskTable";
import StudyFilter from "./StudyFilter";

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
            {displayAsForm} = store.config,
            taskList = store.taskListByStudy,
            noTasks = taskList.length === 0;

        return (
            <div>
                <ScrollToErrorBox error={store.error} />
                <StudyFilter selectFilter={opts => store.filterAndSortStudies(opts)} />
                {noTasks ? <h4>No studies match the given query.</h4> : <TaskTable />}

                {displayAsForm && !noTasks ? (
                    <>
                        <button
                            type="button"
                            onClick={store.submitPatches}
                            className="btn btn-primary">
                            Submit changes
                        </button>
                        <button onClick={store.handleCancel} className="btn space">
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
