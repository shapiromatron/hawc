import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";

import {STATUS} from "../constants";
import StatusIcon from "./StatusIcon";

class StatusSelection extends Component {
    constructor(props) {
        super(props);
        this.state = {status: props.defaultValue};
    }

    render() {
        const choices = _.map(STATUS, (value, key) => {
                return {value: key, display: value.type};
            }),
            {defaultValue, onChange} = this.props,
            id = h.randomString();

        return (
            <div>
                <label className="col-form-label" htmlFor={id}>
                    Status
                </label>
                <select
                    defaultValue={defaultValue}
                    id={id}
                    onChange={event => {
                        let value = parseInt(event.target.value);
                        this.setState({status: value});
                        onChange(value);
                    }}
                    name="status_selection"
                    style={{width: "auto"}}>
                    {choices.map(({value, display}, i) => (
                        <option key={i} value={value}>
                            {display}
                        </option>
                    ))}
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
    defaultValue: PropTypes.number.isRequired,
    onChange: PropTypes.func.isRequired,
};

export default StatusSelection;
