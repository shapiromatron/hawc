import React, { Component } from 'react';
import { connect } from 'react-redux';

import EndpointList from '../components/EndpointList';

import { fetchObjectsIfNeeded, setField } from '../actions/Endpoint';

class Endpoint extends Component {

    componentWillMount() {
        const { dispatch, params } = this.props;
        dispatch(setField(params.field));
        dispatch(fetchObjectsIfNeeded());
    }

    render() {
        let endpoints = this.props.endpoints;
        return <EndpointList endpoints={endpoints} params={this.props.params}/>;
    }
}

function mapStateToProps(state) {
    return {
        endpoints: state.endpoint.items,
    };
}
export default connect(mapStateToProps)(Endpoint);
