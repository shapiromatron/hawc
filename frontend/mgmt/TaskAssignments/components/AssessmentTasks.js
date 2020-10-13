import React, {Component} from "react";
import PropTypes from "prop-types";

import Header from "./Header";
import Task from "./Task";

class AssessmentTasks extends Component {
    render() {
        let headings = [
            {name: "Study", flex: 1},
            {name: "Task", flex: 2},
        ];

        if (this.props.showAssessment) {
            headings.unshift({name: "Assessment", flex: 1});
        }

        return (
            <div style={{padding: "10px"}}>
                <Header headings={headings} />
                {this.props.tasks.map(task => {
                    return (
                        <Task
                            key={task.id}
                            task={task}
                            showAssessment={this.props.showAssessment}
                        />
                    );
                })}
            </div>
        );
    }
}

AssessmentTasks.propTypes = {
    tasks: PropTypes.array.isRequired,
    showAssessment: PropTypes.bool.isRequired,
};

export default AssessmentTasks;
