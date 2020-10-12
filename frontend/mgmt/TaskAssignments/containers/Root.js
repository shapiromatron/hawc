import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import Loading from "shared/components/Loading";

import AssessmentTasks from "../components/AssessmentTasks";
import FinishedTaskFilter from "../components/FinishedTaskFilter";
import RobTasks from "../components/RobTasks";

@inject("store")
@observer
class Root extends Component {
    constructor(props) {
        super(props);
        this.state = {
            filterTasks: true,
            taskFilter: task => {
                return task.status !== 30 && task.status !== 40;
            },
        };
    }

    componentDidMount() {
        this.props.store.fetchTasks();
    }

    render() {
        const {store} = this.props;

        if (store.isFetching || !store.isLoaded) {
            return <Loading />;
        }

        const formatTasks = () => {
                return _.chain(store.tasks)
                    .filter(this.state.taskFilter)
                    .filter(task => task.owner.id === store.config.user)
                    .groupBy(task => task.study.assessment.name)
                    .value();
            },
            groupedTasks = formatTasks(),
            renderTasks = _.keys(groupedTasks).length !== 0,
            // only show assessment header if assessment is unspecified
            showAssessment = store.config.assessment_id === undefined;

        return (
            <div>
                <FinishedTaskFilter
                    checked={this.state.filterTasks}
                    onChange={() => {
                        if (this.state.filterTasks) {
                            this.setState({
                                filterTasks: false,
                                taskFilter: () => true,
                            });
                        } else {
                            this.setState({
                                filterTasks: true,
                                taskFilter: task => task.status !== 30 && task.status !== 40,
                            });
                        }
                    }}
                />
                {renderTasks ? (
                    _.map(groupedTasks, (tasks, key) => (
                        <AssessmentTasks key={key} tasks={tasks} showAssessment={showAssessment} />
                    ))
                ) : (
                    <p className="help-block">There are no tasks available.</p>
                )}
                <RobTasks tasks={store.robTasks} showAssessment={showAssessment} />
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
