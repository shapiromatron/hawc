import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Loading from "shared/components/Loading";

import AssessmentTasks from "../components/AssessmentTasks";

@inject("taskStore")
@observer
class TaskRoot extends Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        this.props.taskStore.fetchTasks();
    }

    render() {
        const store = this.props.taskStore;

        if (store.isFetching || !store.isLoaded) {
            return <Loading />;
        }

        const {tasksByAssessment, hasTasks, showAssessment, filterTasks, toggleFilterTasks} = store;

        return (
            <div>
                <label>
                    <input
                        type="checkbox"
                        name="filter"
                        style={{margin: "4px"}}
                        checked={filterTasks}
                        onChange={toggleFilterTasks}
                    />
                    Hide completed and abandoned tasks
                </label>
                {hasTasks ? (
                    _.map(tasksByAssessment, (tasks, key) => (
                        <AssessmentTasks key={key} tasks={tasks} showAssessment={showAssessment} />
                    ))
                ) : (
                    <p>
                        <i>There are no tasks available.</i>
                    </p>
                )}
            </div>
        );
    }
}

TaskRoot.propTypes = {
    taskStore: PropTypes.object,
};

export default TaskRoot;
