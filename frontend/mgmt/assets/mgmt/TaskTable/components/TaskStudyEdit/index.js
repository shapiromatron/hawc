import React, { Component } from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';

import StudyLabel from 'mgmt/TaskTable/components/StudyLabel';
import TaskForm from 'mgmt/TaskTable/components/TaskForm';

class TaskStudyEdit extends Component {
    constructor(props) {
        super(props);
        this.getChangedData = this.getChangedData.bind(this);
    }

    getChangedData() {
        return _.chain(this.refs)
            .filter((ref) => {
                return ref.formDidChange();
            })
            .map((ref) => {
                return ref.state;
            })
            .value();
    }

    render() {
        const { tasks, study } = this.props.item;
        return (
            <div>
                <hr className="hr-tight" />
                <div className="flexRow-container taskStudy">
                    <StudyLabel study={study} />
                    {tasks.map((task, index) => (
                        <TaskForm
                            key={task.id}
                            ref={`form-${index}`}
                            task={task}
                            className={`task-${index} flex-1`}
                            autocompleteUrl={this.props.autocompleteUrl}
                        />
                    ))}
                </div>
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
    autocompleteUrl: PropTypes.string.isRequired,
};

export default TaskStudyEdit;
