import React, {Component} from "react";
import PropTypes from "prop-types";

class RobTaskRow extends Component {
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
RobTaskRow.propTypes = {
    task: PropTypes.object.isRequired,
    showAssessment: PropTypes.bool.isRequired,
};

export default RobTaskRow;
