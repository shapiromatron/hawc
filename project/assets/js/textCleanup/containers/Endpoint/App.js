import React, { Component } from 'react';
import { connect } from 'react-redux';

import { fetchObjectsIfNeeded } from 'textCleanup/actions/Endpoint';
import EndpointList from 'textCleanup/components/Endpoint/EndpointList';
import Loading from 'textCleanup/components/Loading';


class Endpoint extends Component {

    componentWillMount() {
        this.props.dispatch(fetchObjectsIfNeeded());
    }

    render() {
        if (_.isEmpty(this.props.endpoint.items)) return <Loading />;
        return <EndpointList {...this.props}/>;
    }
}

function mapStateToProps(state) {
    return {
        endpoint: state.endpoint,
    };
}
export default connect(mapStateToProps)(Endpoint);
