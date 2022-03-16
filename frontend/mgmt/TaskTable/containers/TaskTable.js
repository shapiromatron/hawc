import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";
import moment from "moment";

import PopoverTextSpan from "shared/components/PopoverTextSpan";

import {TASK_TYPES, TASK_TYPE_DESCRIPTIONS} from "../constants";
import EditableTask from "../components/EditableTask";

import "./Root.css";

@inject("store")
@observer
class TaskTable extends Component {
    render() {
        const {store} = this.props,
            {userAutocompleteUrl} = store.config,
            taskList = store.taskListByStudy,
            headers = _.zip(_.values(TASK_TYPES), _.values(TASK_TYPE_DESCRIPTIONS));

        return (
            <table className="table table-sm">
                <colgroup>
                    <col width="20%" />
                    <col width="20%" />
                    <col width="20%" />
                    <col width="20%" />
                    <col width="20%" />
                </colgroup>
                <thead>
                    <tr>
                        <th>
                            <PopoverTextSpan
                                text={"Study"}
                                title={"Study"}
                                description={"Selected study object"}
                            />
                        </th>
                        {headers.map((obj, i) => {
                            return (
                                <th key={i}>
                                    <PopoverTextSpan
                                        text={obj[0]}
                                        title={obj[0]}
                                        description={obj[1]}
                                    />
                                </th>
                            );
                        })}
                    </tr>
                </thead>
                <tbody>
                    {taskList.map(obj => {
                        const {study, tasks} = obj;
                        return (
                            <tr key={study.id} className="taskStudyRow">
                                <td>
                                    <a href={study.url}>{study.short_citation}</a>
                                    <br />
                                    <b>Date created: </b>
                                    <span>{moment(study.created).format("L")}</span>
                                </td>
                                {tasks.map(task => {
                                    return (
                                        <td key={task.id}>
                                            <EditableTask
                                                task={task}
                                                userAutocompleteUrl={userAutocompleteUrl}
                                                handleSubmit={data => store.patchTask(data)}
                                            />
                                        </td>
                                    );
                                })}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        );
    }
}

TaskTable.propTypes = {
    store: PropTypes.object,
};

export default TaskTable;
