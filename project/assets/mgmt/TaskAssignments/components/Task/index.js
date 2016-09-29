import React, { Component, PropTypes } from 'react';

import AssessmentLabel from 'mgmt/TaskAssignments/components/AssessmentLabel';
import StudyLabel from 'mgmt/TaskAssignments/components/StudyLabel';
import TaskLabel from 'mgmt/TaskAssignments/components/TaskLabel';


class Task extends Component {
    render() {
        return (
            <div>
                <div className='flexRow-container'>
                    <AssessmentLabel className='flex-1' assessment={this.props.task.study.assessment} />
                    <StudyLabel className='flex-1' study={this.props.task.study}/>
                    <TaskLabel className='flex-2' task={this.props.task} />
                </div>
                <hr style={{margin: '10px 0'}}/>
            </div>
        );
    }
}

Task.propTypes = {
    task: PropTypes.shape({
        study: PropTypes.shape({
            url: PropTypes.string.isRequired,
            short_citation: PropTypes.string.isRequired,
        }).isRequired,
        status_display: PropTypes.string.isRequired,
        type: PropTypes.number.isRequired,
    }).isRequired,
};

export default Task;
