import React, {Component} from "react";
import PropTypes from "prop-types";
import {connect} from "react-redux";
import _ from "lodash";

import {initializeBulkEditForm, patchBulkList, patchDetailList} from "textCleanup/actions/Items";
import Loading from "shared/components/Loading";
import FormComponent from "textCleanup/components/Items/BulkForm";

class BulkForm extends Component {
    constructor(props) {
        super(props);
        this.handleBulkSubmit = this.handleBulkSubmit.bind(this);
        this.handleDetailSubmit = this.handleDetailSubmit.bind(this);
    }

    componentDidMount() {
        this.props.dispatch(
            initializeBulkEditForm(this.getIDs(this.props), this.props.params.field)
        );
    }

    getIDs(props) {
        return _.map(props.items, "id");
    }

    handleBulkSubmit(obj) {
        this.props.dispatch(patchBulkList(obj, this.props.params));
    }

    handleDetailSubmit(obj) {
        this.props.dispatch(patchDetailList(obj, this.props.params));
    }

    isReadyToRender(thisField) {
        let ids = this.getIDs(this.props),
            {params, model} = this.props;

        if (
            (ids && model.editObject == null) ||
            (ids && model.editObject[thisField] == null) ||
            (ids && model.editObject[thisField][params.field] == null)
        ) {
            return false;
        }
        return model.itemsLoaded && model.editObject[thisField][params.field] !== null;
    }

    render() {
        let {items, model, params, config} = this.props,
            modalClass = config[params.type].title,
            thisField = items[0][params.field];
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

function mapStateToProps(state) {
    return {
        config: state.config,
        model: state.items,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        dispatch,
    };
}

BulkForm.propTypes = {
    dispatch: PropTypes.object,
    params: PropTypes.shape({
        field: PropTypes.object,
        type: PropTypes.object,
    }),
    model: PropTypes.shape({
        editObject: PropTypes.object,
        editObjectErrors: PropTypes.object,
        itemsLoaded: PropTypes.object,
    }),
    items: PropTypes.object,
    config: PropTypes.object,
};

export default connect(mapStateToProps, mapDispatchToProps)(BulkForm);
