import React, { Component, PropTypes } from 'react';

import { STATUS } from 'mgmt/TaskTable/constants';


export default class StatusIcon extends Component {

    render() {
        return <i className='fa fa-circle' style={{
            paddingLeft: 5,
            paddingRight: 5,
            color: STATUS[this.props.status].color,
            ...this.props.style,
        }}></i>;
    }
}

StatusIcon.propTypes = {
    status: PropTypes.number.isRequired,
};
