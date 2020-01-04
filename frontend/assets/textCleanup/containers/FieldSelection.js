import React, { Component } from 'react';
import { connect } from 'react-redux';
import _ from 'lodash';

import { fetchModel } from 'textCleanup/actions/Items';
import { fetchAssessment } from 'textCleanup/actions/Assessment';
import FieldList from 'textCleanup/components/FieldList';
import Loading from 'shared/components/Loading';
import urls from 'textCleanup/constants/urls';
import h from 'textCleanup/utils/helpers';

class FieldSelection extends Component {
    componentWillMount() {
        if (!this.props.types) {
            this.props.dispatch(fetchAssessment());
        }
    }

    componentDidMount() {
        this.props.dispatch(fetchModel(this.props.match.params));
    }

    render() {
        if (this.props.objects == undefined || this.props.types == undefined) return <Loading />;
        let { objects, location, types, match } = this.props,
            type = _.find(types, { type: match.params.type }),
            title = h.caseToWords(type.title),
            url = type.url.substr(0, type.url.lastIndexOf(match.params.type));
        h.extendBreadcrumbs(url);

        return (
            <div>
                <h2 className="field_list_title">{`${urls.fields.name} for ${title}`}</h2>
                <FieldList fields={objects} location={location.pathname} />
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        types: state.assessment.active.items,
        objects: state.items.model,
    };
}

export default connect(mapStateToProps)(FieldSelection);
