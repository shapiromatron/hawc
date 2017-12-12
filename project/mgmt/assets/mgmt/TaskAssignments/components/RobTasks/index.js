import React, { Component } from 'react';
import PropTypes from 'prop-types';

import Header from 'mgmt/TaskAssignments/components/Header';
import RobTask from 'mgmt/TaskAssignments/components/RobTask';


class RobTasks extends Component {
    render() {
        let showTasks = this.props.tasks.length !== 0,
            headings = [
                {name: 'Study', flex: 1},
                {name: '', flex: 2},
            ];

        if (this.props.showAssessment){
            headings.unshift({name: 'Assessment', flex: 1});
        }

        return (
            showTasks ?
                <div>
                    <h5>Risk of bias reviews to be completed</h5>
                    <Header headings={headings} />
                    {this.props.tasks.map((task) =>
                        <RobTask key={task.id} task={task} showAssessment={this.props.showAssessment}/>
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
