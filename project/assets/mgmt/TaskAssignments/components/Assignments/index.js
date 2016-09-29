import React, { Component, PropTypes } from 'react';
import _ from 'underscore';

import AssessmentTasks from 'mgmt/TaskAssignments/components/AssessmentTasks';
import Loading from 'shared/components/Loading';
import { fetchTasks } from 'mgmt/TaskAssignments/actions';


class Assignments extends Component {

    componentWillMount() {
        this.props.dispatch(fetchTasks());
    }

    formatTasks() {
        return _.groupBy(this.props.tasks.list, (task) => { return task.study.assessment.name; });
    }

    render() {
        if (!this.props.tasks.isLoaded) return <Loading/>;
        const groupedTasks = this.formatTasks();
        return (
            <div>
                {_.map(groupedTasks, (tasks, key) => {
                    return <AssessmentTasks key={key} name={key} tasks={tasks} />;
                })}
            </div>
        );
    }
}

Assignments.propTypes = {
    dispatch: PropTypes.func.isRequired,
    tasks: PropTypes.shape({
        list: PropTypes.array.isRequired,
    }).isRequired,
};

export default Assignments;
