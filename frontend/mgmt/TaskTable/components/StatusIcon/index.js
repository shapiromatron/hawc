import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { STATUS } from 'mgmt/TaskTable/constants';

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
};
