import React, {Component} from "react";
import PropTypes from "prop-types";

class TaskRow extends Component {
    render() {
        const {assessment} = this.props.task.scores[0].metric.domain,
            {study_name, study_id, url_edit} = this.props.task.scores[0],
            robText = this.props.task.final ? "Edit final review" : "Edit review";

        return (
            <tr>
                {this.props.showAssessment ? (
                    <td>
                        <a href={assessment.url}>{assessment.name}</a>
                    </td>
                ) : null}
                <td>
                    <a href={`/study/${study_id}/`}>{study_name}</a>
                </td>
                <td>
                    <a className="btn" href={url_edit}>
                        <i className="fa fa-edit" /> {robText}
                    </a>
                </td>
            </tr>
        );
    }
}
TaskRow.propTypes = {
    task: PropTypes.object.isRequired,
    showAssessment: PropTypes.bool.isRequired,
};

class RobTasks extends Component {
    render() {
        const {tasks, showAssessment} = this.props,
            hasTasks = this.props.tasks.length > 0;
        return (
            <div>
                <h4>Pending risk of bias/study evaluation reviews</h4>
                {hasTasks ? (
                    <table className="table table-condensed table-striped">
                        <colgroup>
                            {showAssessment ? <col width="33%" /> : null}
                            <col width="33%" />
                            <col width="66%" />
                        </colgroup>
                        <thead>
                            <tr>
                                {showAssessment ? <th>Assessment</th> : null}
                                <th>Study</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tasks.map((task, i) => (
                                <TaskRow showAssessment={showAssessment} task={task} key={i} />
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p>
                        <i>You have no outstanding reviews.</i>
                    </p>
                )}
            </div>
        );
    }
}
RobTasks.propTypes = {
    tasks: PropTypes.array,
    showAssessment: PropTypes.bool,
};

export default RobTasks;
