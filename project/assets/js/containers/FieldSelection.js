import React, { Component } from 'react';
import { connect } from 'react-redux';

import FieldList from 'components/FieldList';
import Loading from 'components/Loading';
import urls from 'constants/urls';
import h from 'utils/helpers';

import { setType, fetchModelIfNeeded } from 'actions/Endpoint';

class FieldSelection extends Component {

    componentWillMount() {
        const { dispatch, params } = this.props;
        dispatch(setType(params.type));
        dispatch(fetchModelIfNeeded());
    }

    render() {
        if(this.props.objects == undefined) return <Loading />;
        let { objects, location, types, params } = this.props,
            type = _.findWhere(types, {type: params.type}),
            title = h.caseToWords(type.title),
            url_list = [{
                url: type.url.substr(0, type.url.lastIndexOf(params.type)),
                title: title.substr(0, title.lastIndexOf(' '))}];
        h.extendBreadcrumbs(url_list);

        return (
            <div>
                <h2 className='field_list_title'>
                    {`${urls.fields.name} for ${title}`}
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
