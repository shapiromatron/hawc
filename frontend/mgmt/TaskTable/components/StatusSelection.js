import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
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
            <div className="form-group">
                <label htmlFor={id}>Status</label>
                <div className="input-group">
                    <select
                        className="form-control"
                        defaultValue={defaultValue}
                        id={id}
                        onChange={event => {
                            let value = parseInt(event.target.value);
                            this.setState({status: value});
                            onChange(value);
                        }}
                        name="status_selection">
                        {choices.map(({value, display}, i) => (
                            <option key={i} value={value}>
                                {display}
                            </option>
                        ))}
                    </select>
                    <div className="input-group-append">
                        <span className="input-group-text">
                            <StatusIcon
                                status={this.state.status}
                                style={{
                                    height: "20px",
                                    verticalAlign: "middle",
                                    padding: "5px",
                                }}
                            />
                        </span>
                    </div>
                </div>
            </div>
        );
    }
}

StatusSelection.propTypes = {
    defaultValue: PropTypes.number.isRequired,
    onChange: PropTypes.func.isRequired,
};

export default StatusSelection;
