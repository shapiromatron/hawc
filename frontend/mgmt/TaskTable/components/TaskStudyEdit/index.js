import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import StudyLabel from "mgmt/TaskTable/components/StudyLabel";
import TaskForm from "mgmt/TaskTable/components/TaskForm";

class TaskStudyEdit extends Component {
    constructor(props) {
        super(props);
        this.getChangedData = this.getChangedData.bind(this);
    }

    getChangedData() {
        return _.chain(this.components)
            .filter(component => component != null)
            .filter(component => {
                return component.formDidChange();
            })
            .map(component => {
                return component.state;
            })
            .value();
    }

    render() {
        const {tasks, study} = this.props.item;

        this.components = [];

        return (
            <div>
                <hr className="hr-tight" />
                <div className="flexRow-container taskStudy">
                    <StudyLabel study={study} />
                    {tasks.map((task, index) => (
                        <TaskForm
                            key={task.id}
                            ref={c => this.components.push(c)}
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
