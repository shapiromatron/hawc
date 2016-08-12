import React, { Component } from 'react';
import { connect } from 'react-redux';

import {
    initializeBulkEditForm,
    patchBulkList,
    patchDetailList,
} from 'textCleanup/actions/Items';
import Loading from 'shared/components/Loading';
import FormComponent from 'textCleanup/components/Items/BulkForm';


class BulkForm extends Component {

    constructor(props) {
        super(props);
        this.handleBulkSubmit = this.handleBulkSubmit.bind(this);
        this.handleDetailSubmit = this.handleDetailSubmit.bind(this);
    }

    componentWillMount() {
        this.props.dispatch(initializeBulkEditForm(this.getIDs(this.props), this.props.field));
    }

    getIDs(props) {
        return _.pluck(props.items, 'id');
    }

    handleBulkSubmit(obj) {
        this.props.dispatch(patchBulkList(obj));
    }

    handleDetailSubmit(obj) {
        this.props.dispatch(patchDetailList(obj));
    }

    isReadyToRender(thisField){
        let ids = this.getIDs(this.props),
            { field, model } = this.props;


        if (ids && model.editObject == null ||
            ids && model.editObject[thisField] == null ||
            ids && model.editObject[thisField][field] == null){
            return false;
        }
        return (model.itemsLoaded && model.editObject[thisField][field] !== null);
    }

    render() {
        let { items, model, field, params, config } = this.props,
            modalClass = config[params.type].title,
            thisField = items[0][field];
        if (!this.isReadyToRender(thisField)) return <Loading />;
        this.isRendered = true;
        return (
            <FormComponent
                items={items}
                object={model.editObject[thisField]}
                errors={model.editObjectErrors}
                field={thisField}
                handleBulkSubmit={this.handleBulkSubmit}
                handleDetailSubmit={this.handleDetailSubmit}
                params={params}
                modalClass={modalClass}
            />

        );
    }

}

function mapStateToProps(state){
    return {
        config: state.config,
        params: state.router.params,
        model: state.items,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        dispatch,
    };
}
export default connect(mapStateToProps, mapDispatchToProps)(BulkForm);
