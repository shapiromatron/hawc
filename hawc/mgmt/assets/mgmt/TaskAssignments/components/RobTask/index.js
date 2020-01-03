import React, { Component } from 'react';
import PropTypes from 'prop-types';

import AssessmentLabel from 'mgmt/TaskAssignments/components/AssessmentLabel';

class RobTask extends Component {
    render() {
        let { assessment } = this.props.task.scores[0].metric.domain,
            { study_name, study_id, url_edit } = this.props.task.scores[0],
            robText = this.props.task.final ? 'Edit final review' : 'Edit review',
            assessmentLbl = this.props.showAssessment ? (
                <AssessmentLabel className="flex-1" assessment={assessment} />
            ) : null;

        return (
            <div>
                <hr className="hr-tight" />
                <div className="flexRow-container">
                    {assessmentLbl}
                    <span className="flex-1">
                        <a href={`/study/${study_id}/`}>{study_name}</a>
                    </span>
                    <span className="flex-2">
                        <a href={url_edit} title="Edit this review">
                            <i className="fa fa-edit" /> {robText}
                        </a>
                    </span>
                </div>
            </div>
        );
    }
}

RobTask.propTypes = {
    task: PropTypes.object.isRequired,
};

export default RobTask;
