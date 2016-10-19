import React, { Component, PropTypes } from 'react';

import Header from 'mgmt/TaskAssignments/components/Header';
import Task from 'mgmt/TaskAssignments/components/Task';


class AssessmentTasks extends Component {
    render() {
        let headings = [
            {name: 'Study', flex: 1},
            {name: 'Task', flex: 2},
        ];

        if (this.props.showAssessment){
            headings.unshift({name: 'Assessment', flex: 1});
        }

        return (
            <div style={{padding: '10px'}}>
            <Header headings={headings} />
            {this.props.tasks.map((task) => {
                return <Task key={task.id} task={task} showAssessment={this.props.showAssessment}/>;
            })}
            </div>
        );
    }
}

AssessmentTasks.propTypes = {
    name: PropTypes.string.isRequired,
    tasks: PropTypes.array.isRequired,
    showAssessment: PropTypes.bool.isRequired,
};

export default AssessmentTasks;
