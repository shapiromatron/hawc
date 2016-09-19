import React, { Component, PropTypes } from 'react';

import { STATUS } from 'mgmt/TaskTable/constants';


export default class StatusIcon extends Component {

    render() {
        return (<i className='fa fa-circle' style={{color: STATUS[this.props.status].color}}></i>);
    }
}

StatusIcon.propTypes = {
    status: PropTypes.number.isRequired,
};
