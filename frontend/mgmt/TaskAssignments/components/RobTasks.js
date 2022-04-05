import _ from "lodash";

import React, {Component} from "react";
import PropTypes from "prop-types";

import RobTaskRow from "./RobTaskRow";

class RobTasks extends Component {
    render() {
        const {tasks, studies, showAssessment} = this.props,
            hasTasks = this.props.tasks.length > 0;
        return (
            <div>
                <h4>Pending risk of bias/study evaluation reviews</h4>
                {hasTasks ? (
                    <table className="table table-sm table-striped">
                        <colgroup>
                            {showAssessment ? <col width="33%" /> : null}
                            <col width="33%" />
                            <col width="66%" />
                        </colgroup>
                        <thead>
                            <tr>
                                {showAssessment ? <th>Assessment</th> : null}
                                <th>Study</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tasks.map((task, i) => {
                                let study = _.find(studies, s => s.id == task.study);
                                return (
                                    <RobTaskRow
                                        showAssessment={showAssessment}
                                        task={task}
                                        study={study}
                                        key={i}
                                    />
                                );
                            })}
                        </tbody>
                    </table>
                ) : (
                    <p>
                        <i>You have no outstanding reviews.</i>
                    </p>
                )}
            </div>
        );
    }
}
RobTasks.propTypes = {
    tasks: PropTypes.array,
    studies: PropTypes.array,
    showAssessment: PropTypes.bool,
};

export default RobTasks;
