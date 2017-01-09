import React, { Component } from 'react';
import { connect } from 'react-redux';
import _ from 'underscore';

import AssessmentTasks from 'mgmt/TaskAssignments/components/AssessmentTasks';
import Loading from 'shared/components/Loading';
import { fetchTasks } from 'mgmt/TaskAssignments/actions';


class Assignments extends Component {

    componentWillMount() {
        this.props.dispatch(fetchTasks());
    }

    formatTasks() {
        return _.chain(this.props.tasks.list)
                .filter((task) => task.owner.id == this.props.config.user)
                .groupBy((task) => { return task.study.assessment.name; })
                .value();
    }

    renderNoTasks() {
        return <p className="help-block">There are no tasks available.</p>;
    }

    render() {
        if (!this.props.tasks.isLoaded) return <Loading/>;
        const groupedTasks = this.formatTasks();

        if (_.keys(groupedTasks).length === 0 ){
            return this.renderNoTasks();
        }

        // only show assessment header if assessment is unspecified
        let showAssessment = (this.props.config.assessment_id === undefined);

        return (
            <div>
                {_.map(groupedTasks, (tasks, key) => {
                    return <AssessmentTasks key={key} name={key} tasks={tasks} showAssessment={showAssessment} />;
                })}
            </div>
        );
    }
}

function mapStateToProps(state){
    const { config, tasks } = state;
    return {
        config,
        tasks,
    };
}

export default connect(mapStateToProps)(Assignments);
