import React, { Component, PropTypes } from 'react';

import Header from 'mgmt/TaskAssignments/components/Header';
import Task from 'mgmt/TaskAssignments/components/Task';


class AssessmentTasks extends Component {
    render() {
        const headings = [
            {name: 'Assessment', flex: 1},
            {name: 'Study', flex: 1},
            {name: 'Task', flex: 2},
        ];
        return (
            <div style={{padding: '10px'}}>
            <Header headings={headings} />
            {this.props.tasks.map((task) => {
                return <Task key={task.id} task={task}/>;
            })}
            </div>
        );
    }
}

AssessmentTasks.propTypes = {
    name: PropTypes.string.isRequired,
    tasks: PropTypes.array.isRequired,
};

export default AssessmentTasks;
