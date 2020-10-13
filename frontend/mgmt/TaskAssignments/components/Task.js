import React, {Component} from "react";
import PropTypes from "prop-types";

import TaskToggle from "mgmt/TaskTable/components/TaskToggle";

import AssessmentLabel from "./AssessmentLabel";
import StudyLabel from "./StudyLabel";
import TaskLabel from "./TaskLabel";

class Task extends Component {
    render() {
        let assessmentLbl = this.props.showAssessment ? (
            <AssessmentLabel className="flex-1" assessment={this.props.task.study.assessment} />
        ) : null;

        return (
            <div>
                <hr className="hr-tight" />
                <div className="flexRow-container">
                    {assessmentLbl}
                    <StudyLabel className="flex-1" study={this.props.task.study} />
                    <TaskToggle TaskLabel={TaskLabel} className="flex-2" task={this.props.task} />
                </div>
            </div>
        );
    }
}

Task.propTypes = {
    task: PropTypes.shape({
        study: PropTypes.shape({
            url: PropTypes.string.isRequired,
            short_citation: PropTypes.string.isRequired,
            assessment: PropTypes.object,
        }).isRequired,
        status_display: PropTypes.string.isRequired,
        type: PropTypes.number.isRequired,
    }).isRequired,
    showAssessment: PropTypes.bool.isRequired,
};

export default Task;
