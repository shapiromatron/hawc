import PropTypes from "prop-types";
import React, {Component} from "react";

import TaskRow from "../containers/TaskRow";

class AssessmentTasks extends Component {
    render() {
        const {showAssessment, tasks} = this.props,
            {assessment} = tasks[0].study;
        return (
            <>
                {showAssessment ? (
                    <h4>
                        {assessment.name}&nbsp;
                        <a className="btn btn-sm btn-primary" href={assessment.url}>
                            View
                        </a>
                    </h4>
                ) : null}
                <table className="table table-sm table-striped">
                    <colgroup>
                        <col width="30%" />
                        <col width="70%" />
                    </colgroup>
                    <thead>
                        <tr>
                            <th>Study</th>
                            <th>Task</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tasks.map(task => (
                            <TaskRow key={task.id} task={task} />
                        ))}
                    </tbody>
                </table>
            </>
        );
    }
}

AssessmentTasks.propTypes = {
    tasks: PropTypes.array.isRequired,
    showAssessment: PropTypes.bool.isRequired,
};

export default AssessmentTasks;
