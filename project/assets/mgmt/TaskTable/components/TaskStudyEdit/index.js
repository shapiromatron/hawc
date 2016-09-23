import React, { Component, PropTypes } from 'react';
import _ from 'underscore';

import StudyLabel from 'mgmt/TaskTable/components/StudyLabel';
import TaskForm from 'mgmt/TaskTable/components/TaskForm';


class TaskStudyEdit extends Component {

    constructor(props) {
        super(props);
        this.getChangedData = this.getChangedData.bind(this);
    }

    getChangedData() {
        return _.chain(this.refs)
                .filter((ref) => { return ref.formDidChange(); })
                .map((ref) => { return ref.state; })
                .value();
    }

    render() {
        const { tasks, study } = this.props.item;
        return (
            <div>
                <div className='flexRow-container taskStudy'>
                    <StudyLabel study={study} />
                    {tasks.map((task, index) => (
                        <TaskForm ref={`form-${index}`} key={task.id} task={task} className={`task-${index} flex-1`}/>
                    ))}
                </div>
                <hr/>
            </div>
        );
    }
}

TaskStudyEdit.propTypes = {
    item: PropTypes.shape({
        study: PropTypes.shape({
            short_citation: PropTypes.string.isRequired,
        }).isRequired,
        tasks: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.number.isRequired,
                owner: PropTypes.object,
                status: PropTypes.number.isRequired,
                status_display: PropTypes.string.isRequired,
            })
        ).isRequired,
    }),
};

export default TaskStudyEdit;
