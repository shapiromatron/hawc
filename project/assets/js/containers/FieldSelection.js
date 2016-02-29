import React, { Component } from 'react';
import { connect } from 'react-redux';

import { fetchModelIfNeeded } from 'actions/Endpoint';
import FieldList from 'components/FieldList';
import Loading from 'components/Loading';
import urls from 'constants/urls';
import h from 'utils/helpers';


class FieldSelection extends Component {

    componentWillMount() {
        this.props.dispatch(fetchModelIfNeeded());
    }

    render() {
        if(this.props.objects == undefined) return <Loading />;
        let { objects, location, types, params } = this.props,
            type = _.findWhere(types, {type: params.type}),
            title = h.caseToWords(type.title),
            url = type.url.substr(0, type.url.lastIndexOf(params.type));
        h.extendBreadcrumbs(url);

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
