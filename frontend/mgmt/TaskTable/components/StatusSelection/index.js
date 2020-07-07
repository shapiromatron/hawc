import React, {Component} from "react";
import PropTypes from "prop-types";

import {STATUS} from "mgmt/TaskTable/constants";
import StatusIcon from "mgmt/TaskTable/components/StatusIcon";

class StatusSelection extends Component {
    constructor(props) {
        super(props);
        this.state = {status: props.task.status};
        this.getSelection = this.getSelection.bind(this);
    }

    getStatusChoices() {
        return Object.keys(STATUS).map(status => {
            return {value: status, display: STATUS[status].type};
        });
    }

    getSelection({target}) {
        let value = parseInt(target.value);
        this.setState({status: value});
        this.props.onChange(value);
    }

    render() {
        const choices = this.getStatusChoices(),
            idName = `${this.props.task.id}-status_selection`;
        return (
            <div>
                <label className="control-label" htmlFor={idName}>
                    Status
                </label>
                <select
                    defaultValue={this.props.task.status}
                    id={idName}
                    onChange={this.getSelection}
                    name="status_selection"
                    style={{width: "auto"}}>
                    {choices.map(({value, display}, i) => {
                        return (
                            <option key={i} value={value}>
                                {display}
                            </option>
                        );
                    })}
                </select>
                <StatusIcon
                    status={this.state.status}
                    style={{
                        height: "25px",
                        verticalAlign: "middle",
                        padding: "5px",
                    }}
                />
            </div>
        );
    }
}

StatusSelection.propTypes = {
    task: PropTypes.shape({
        id: PropTypes.number.isRequired,
        status: PropTypes.object,
    }).isRequired,
    onChange: PropTypes.func.isRequired,
};

export default StatusSelection;
