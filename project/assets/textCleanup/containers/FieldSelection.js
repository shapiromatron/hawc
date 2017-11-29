import React, { Component } from 'react';
import { connect } from 'react-redux';
import _ from 'lodash';

import { fetchModelIfNeeded } from 'textCleanup/actions/Items';
import FieldList from 'textCleanup/components/FieldList';
import Loading from 'shared/components/Loading';
import urls from 'textCleanup/constants/urls';
import h from 'textCleanup/utils/helpers';


class FieldSelection extends Component {

    componentWillMount() {
        this.props.dispatch(fetchModelIfNeeded());
    }

    render() {
        if(this.props.objects == undefined) return <Loading />;
        let { objects, location, types, params } = this.props,
            type = _.find(types, {type: params.type}),
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
        objects: state.items.model,
    };
}

export default connect(mapStateToProps)(FieldSelection);
