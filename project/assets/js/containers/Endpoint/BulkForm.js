import React, { Component } from 'react';
import { connect } from 'react-redux';

import h from 'utils/helpers';
import Loading from 'components/Loading';
import FormComponent from 'components/Endpoint/BulkForm';
import 'containers/Endpoint/EndpointBulkForm.css';

import {
    initializeBulkEditForm,
    patchObjectList,
} from 'actions/Endpoint';

export default class BulkForm extends Component {

    componentWillMount() {
        let ids = this.getIDs();
        this.props.dispatch(initializeBulkEditForm(ids, this.props.field));
    }

    getIDs(){
        return _.pluck(this.props.items, 'id');
    }

    handleSubmit(obj) {
        this.props.dispatch(patchObjectList([obj]));
    }

    isReadyToRender(thisField){
        let ids = this.getIDs(),
            { field, model } = this.props;

        if (ids && model.editObject == null ||
            ids && model.editObject[thisField] == null ||
            ids && model.editObject[thisField][field] == null){
            return false;
        }
        return (model.itemsLoaded && model.editObject[thisField][field] !== null);
    }

    render() {
        let { items, model, field, params } = this.props,
            thisField = items[0][field];
        if (!this.isReadyToRender(thisField)) return <Loading />;
        this.isRendered = true;
        return (
            <FormComponent
                object={model.editObject[thisField]}
                errors={model.editObjectErrors}
                field={thisField}
                handleSubmit={this.handleSubmit.bind(this)}
                params={params}
            />

        );
    }

}

function mapStateToProps(state){
    return {
        params: state.router.params,
        model: state.endpoint,
        itemsLoaded: state.endpoint.itemsLoaded,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        dispatch,
    };
}
export default connect(mapStateToProps, mapDispatchToProps)(BulkForm);
