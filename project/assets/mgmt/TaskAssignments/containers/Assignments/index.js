import React, { Component } from 'react';
import { connect } from 'react-redux';
import _ from 'underscore';

import AssessmentTasks from 'mgmt/TaskAssignments/components/AssessmentTasks';
import FinishedTaskFilter from 'mgmt/TaskAssignments/components/FinishedTaskFilter';
import Loading from 'shared/components/Loading';
import { fetchTasks } from 'mgmt/TaskAssignments/actions';


class Assignments extends Component {
    constructor(props) {
        super(props);
        this.toggleFilter = this.toggleFilter.bind(this);
        this.state = {
            filterTasks: true,
            taskFilter:  (task) => {return task.status !== 30 && task.status !== 40;},
        };
    }


    componentWillMount() {
        this.props.dispatch(fetchTasks());
    }

    formatTasks() {
        return _.chain(this.props.tasks.list)
                .filter(this.state.taskFilter)
                .filter((task) => task.owner.id == this.props.config.user)
                .groupBy((task) => { return task.study.assessment.name; })
                .value();
    }

    toggleFilter() {
        if (this.state.filterTasks){
            this.setState({
                filterTasks: false,
                taskFilter: () => true,
            });
        } else {
            this.setState({
                filterTasks: true,
                taskFilter: (task) => {return task.status !== 30 && task.status !== 40;},
            });
        }
    }

    renderNoTasks() {
        return <p className="help-block">There are no tasks available.</p>;
    }

    render() {
        if (!this.props.tasks.isLoaded) return <Loading/>;
        const groupedTasks = this.formatTasks();

        // only show assessment header if assessment is unspecified
        let showAssessment = (this.props.config.assessment_id === undefined);

        return (
            <div>
                <FinishedTaskFilter checked={this.state.filterTasks} onChange={this.toggleFilter} />
                {_.keys(groupedTasks).length === 0 ?
                    this.renderNoTasks() :
                    _.map(groupedTasks, (tasks, key) => {
                        return <AssessmentTasks key={key} tasks={tasks} showAssessment={showAssessment} />;
                    })
                }
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
