import React, { Component } from 'react';
import { connect } from 'react-redux';

import FieldList from '../components/FieldList';
import Loading from '../components/Loading';

import { setType, fetchModelIfNeeded } from '../actions/Endpoint';

class Fields extends Component {

    componentWillMount() {
        const { dispatch, params } = this.props;
        dispatch(setType(params.type))
        dispatch(fetchModelIfNeeded());
    }

    render() {
        if(this.props.objects == undefined) return <Loading />;
        return <FieldList fields={this.props.objects} />;
    }
}

function mapStateToProps(state){
    return {
        objects: state.endpoint.model,
    };
}

export default connect(mapStateToProps)(Fields);
