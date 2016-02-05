import React, { Component } from 'react';
import { connect } from 'react-redux';

import List from 'components/Endpoint/List';
import Loading from 'components/Loading';
import h from 'utils/helpers';

import { fetchObjectsIfNeeded, setField } from 'actions/Endpoint';

class Endpoint extends Component {

    componentWillMount() {
        const { dispatch, params } = this.props;
        dispatch(setField(params.field));
        dispatch(fetchObjectsIfNeeded());
    }

    render() {
        if (_.isEmpty(this.props.endpoint.items)) return <Loading />;
        let { endpoint, params } = this.props;
        return <List endpoint={endpoint} params={params}/>;
    }
}

function mapStateToProps(state) {
    return {
        endpoint: state.endpoint,
    };
}
export default connect(mapStateToProps)(Endpoint);
