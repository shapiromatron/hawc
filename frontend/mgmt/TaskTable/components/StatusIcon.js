import {STATUS} from "mgmt/TaskTable/constants";
import PropTypes from "prop-types";
import React, {Component} from "react";

export default class StatusIcon extends Component {
    render() {
        return (
            <i
                className="fa fa-circle"
                style={{
                    paddingLeft: 5,
                    paddingRight: 5,
                    color: STATUS[this.props.status].color,
                    ...this.props.style,
                }}
            />
        );
    }
}

StatusIcon.propTypes = {
    status: PropTypes.number.isRequired,
    style: PropTypes.object,
};
