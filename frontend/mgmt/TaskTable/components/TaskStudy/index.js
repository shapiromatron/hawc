import React, {Component} from "react";
import PropTypes from "prop-types";

import StudyLabel from "mgmt/TaskTable/components/StudyLabel";
import TaskLabel from "mgmt/TaskTable/components/TaskLabel";
import TaskToggle from "mgmt/TaskTable/containers/TaskToggle";

class TaskStudy extends Component {
    render() {
        const {tasks, study} = this.props.item;
        return (
            <div>
                <hr className="hr-tight" />
                <div className="flexRow-container taskStudy">
                    <StudyLabel study={study} />
                    {tasks.map((task, index) => (
                        <TaskToggle
                            TaskLabel={TaskLabel}
                            key={task.id}
                            task={task}
                            className={`task-${index} flex-1`}
                        />
                    ))}
                </div>
            </div>
        );
    }
}

TaskStudy.propTypes = {
    item: PropTypes.shape({
        study: PropTypes.shape({
            short_citation: PropTypes.string.isRequired,
        }).isRequired,
        tasks: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.number.isRequired,
                owner: PropTypes.object,
                status: PropTypes.number.isRequired,
                status_display: PropTypes.string.isRequired,
            })
        ).isRequired,
    }),
};

export default TaskStudy;
