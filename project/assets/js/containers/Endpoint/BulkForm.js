import React from 'react';
import { connect } from 'react-redux';
import PureComponent from 'react-pure-render/component';

import Loading from 'components/Loading';
import FormComponent from 'components/Endpoint/BulkForm';
import 'containers/Endpoint/EndpointBulkForm.css';

import {
    initializeBulkEditForm,
    patchBulkList,
    patchDetailList,
} from 'actions/Endpoint';

export default class BulkForm extends PureComponent {

    componentWillMount() {
        this.props.dispatch(initializeBulkEditForm(this.getIDs(this.props), this.props.field));
    }

    shouldComponentUpdate(nextProps, nextState) {
        let IDs = this.getIDs(this.props),
            nextIDs = _.pluck(nextProps.items, 'id'),
            { field, model, items } = this.props,
            thisField = items[0][field];
        return (
            !_.isEqual(IDs, nextIDs) ||
            model.editObject == null ||
            model.editObject[thisField] == null
        );
    }

    componentWillUpdate(nextProps) {
      this.props.dispatch(initializeBulkEditForm(this.getIDs(nextProps), this.props.field));
    }

    getIDs(props) {
        return _.pluck(props.items, 'id');
    }

    handleBulkSubmit(obj) {
        this.props.dispatch(patchBulkList([obj]));
    }

    handleDetailSubmit(obj) {
        this.props.dispatch(patchDetailList([obj]));
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
            modelEndpoint = config[params.type].endpoint,
            thisField = items[0][field];
        if (!this.isReadyToRender(thisField)) return <Loading />;
        this.isRendered = true;
        return (
            <FormComponent
                items={items}
                object={model.editObject[thisField]}
                errors={model.editObjectErrors}
                field={thisField}
                handleBulkSubmit={this.handleBulkSubmit.bind(this)}
                handleDetailSubmit={this.handleDetailSubmit.bind(this)}
                params={params}
                modelEndpoint={modelEndpoint}
            />

        );
    }

}

function mapStateToProps(state){
    return {
        config: state.config,
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
