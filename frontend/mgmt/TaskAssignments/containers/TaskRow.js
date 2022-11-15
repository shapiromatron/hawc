import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import EditableTask from "../../TaskTable/components/EditableTask";

@inject("taskStore")
@observer
class TaskRow extends Component {
    render() {
        const {study} = this.props.task,
            {config, patchTask} = this.props.taskStore;

        return (
            <tr>
                <td>
                    <a href={study.url}>{study.short_citation}</a>
                </td>
                <td>
                    <EditableTask
                        task={this.props.task}
                        showOwner={false}
                        userAutocompleteUrl={config.autocomplete.url}
                        handleSubmit={updates => patchTask(updates)}
                    />
                </td>
            </tr>
        );
    }
}

TaskRow.propTypes = {
    task: PropTypes.shape({
        study: PropTypes.shape({
            url: PropTypes.string.isRequired,
            short_citation: PropTypes.string.isRequired,
            assessment: PropTypes.object,
        }).isRequired,
        status_display: PropTypes.string.isRequired,
        type: PropTypes.number.isRequired,
    }).isRequired,
    taskStore: PropTypes.object,
};

export default TaskRow;
