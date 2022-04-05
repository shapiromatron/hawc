import React, {Component} from "react";
import PropTypes from "prop-types";

class RobTaskRow extends Component {
    render() {
        const {task, study} = this.props,
            {assessment} = study,
            robText = task.final ? "Edit final review" : "Edit review";

        return (
            <tr>
                {this.props.showAssessment ? (
                    <td>
                        <a href={assessment.url}>{assessment.name}</a>
                    </td>
                ) : null}
                <td>
                    <a href={`/study/${study.id}/`}>{study.short_citation}</a>
                </td>
                <td>
                    <a className="btn btn-light" href={`/rob/${task.id}/update/`}>
                        <i className="fa fa-edit" /> {robText}
                    </a>
                </td>
            </tr>
        );
    }
}
RobTaskRow.propTypes = {
    task: PropTypes.object.isRequired,
    study: PropTypes.object.isRequired,
    showAssessment: PropTypes.bool.isRequired,
};

export default RobTaskRow;
