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
        console.log(this.props)
        if (_.isEmpty(this.props.endpoint.items)) return <Loading />;
        let { endpoint, endpoint_types, params } = this.props,
            type = _.findWhere(endpoint_types, {type: params.type}),
            title = h.caseToWords(type.title),
            url_list = [{
                url: type.url.substr(0, endpoint_types.lastIndexOf(params.type)),
                title: title.substr(0, title.lastIndexOf(' ')),
            }, {
                url: type.url,
                title: h.caseToWords(endpoint.field),
            }];
        h.extendBreadcrumbs(url_list);
        return <List endpoint={endpoint} params={this.props.params}/>;
    }
}

function mapStateToProps(state) {
    return {
        endpoint_types: state.assessment.active.items,
        endpoint: state.endpoint,
    };
}
export default connect(mapStateToProps)(Endpoint);
