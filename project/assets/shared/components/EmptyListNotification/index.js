import React, { Component, PropTypes } from 'react';


class EmptyListNotification extends Component {
    render() {
        return (<h4>{`No ${this.props.listItem} match the given query`}</h4>);
    }
}

EmptyListNotification.propTypes = {
    listItem: PropTypes.string.isRequired,
};

export default EmptyListNotification;
