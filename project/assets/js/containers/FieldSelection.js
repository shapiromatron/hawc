import React, { Component } from 'react';
import { connect } from 'react-redux';

import FieldList from '../components/FieldList';
import Loading from '../components/Loading';
import urls from '../constants/urls';
import h from '../utils/helpers';

import { setType, fetchModelIfNeeded } from '../actions/Endpoint';

class FieldSelection extends Component {

    componentWillMount() {
        const { dispatch, params } = this.props;
        dispatch(setType(params.type));
        dispatch(fetchModelIfNeeded());
    }

    render() {
        if(this.props.objects == undefined) return <Loading />;
        let { objects, location, types, params } = this.props,
            type = _.findWhere(types, {type: params.type});
        return (
            <div>
                <h2 className='field_list_title'>
                    {`${urls.fields.name} for ${h.caseToWords(type.title)}`}
                </h2>
                <FieldList fields={objects} location={location.pathname}/>
            </div>
        );
    }
}

function mapStateToProps(state){
    return {
        types: state.assessment.active.items,
        objects: state.endpoint.model,
    };
}

export default connect(mapStateToProps)(FieldSelection);
