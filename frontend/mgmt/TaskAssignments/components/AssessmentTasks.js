import React, {Component} from "react";
import PropTypes from "prop-types";

import Task from "./Task";

class AssessmentTasks extends Component {
    render() {
        const {showAssessment, tasks} = this.props,
            {assessment} = tasks[0].study;
        return (
            <>
                {showAssessment ? (
                    <h4>
                        {assessment.name}&nbsp;
                        <a className="btn btn-small btn-link" href={assessment.url}>
                            View
                        </a>
                    </h4>
                ) : null}
                <table className="table table-condensed table-striped">
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
                            <Task key={task.id} task={task} />
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
