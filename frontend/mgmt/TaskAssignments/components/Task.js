import React, {Component} from "react";
import PropTypes from "prop-types";

// import TaskToggle from "mgmt/TaskTable/components/TaskToggle";
// import TaskLabel from "./TaskLabel";

class Task extends Component {
    render() {
        const {study} = this.props.task;
        return (
            <tr>
                <td>
                    <a href={study.url}>{study.short_citation}</a>
                </td>
                <td>TODO - add TaskToggle</td>
                {/* <TaskToggle TaskLabel={TaskLabel} className="flex-2" task={this.props.task} /> */}
            </tr>
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
};

export default Task;
