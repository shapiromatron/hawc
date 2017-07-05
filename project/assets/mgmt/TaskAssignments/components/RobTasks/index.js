import React, { Component, PropTypes } from 'react';

import RobTask from 'mgmt/TaskAssignments/components/RobTask';


class RobTasks extends Component {
    render() {
        let showTasks = this.props.tasks.length !== 0;
        return (
            showTasks ?
                <div>
                    <h5>Risk of Bias reviews to be completed</h5>
                    <div className='flexRow-container'>
                        <span className='flex-1'><b>Assessment</b></span>
                        <span className='flex-1'><b>Study</b></span>
                        <span className='flex-2'></span>
                    </div>
                    {this.props.tasks.map((task) =>
                        <RobTask key={task.id} task={task}/>
                    )}
                </div>:
                null
        );
    }
}

RobTasks.propTypes = {
    tasks: PropTypes.array,
};

export default RobTasks;
