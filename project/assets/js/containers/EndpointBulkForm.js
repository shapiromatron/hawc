import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';

import h from '../utils/helpers';
import Loading from '../components/Loading';
import FormFieldError from '../components/FormFieldError';
import '../../css/EndpointBulkForm.css';

import {
    initializeBulkEditForm,
} from '../actions/Endpoint';

export default class EndpointBulkForm extends Component {

    componentWillMount() {
        let ids = this.getIDs();
        this.props.dispatch(initializeBulkEditForm(ids, this.props.field));
    }

    getIDs(){
        return _.pluck(this.props.items, 'id');
    }

    handleChange(e) {
        let obj = {};
        obj[e.target.name] = h.getValue(e.target);
        this.setState({editObject: obj});
    }

    handleSubmit() {
        ids = _.map(groupedEndpoints, (group) => {
            return _.pluck(group, 'id');
        });
    }

    isReadyToRender(thisField){
        let ids = this.getIDs(),
            { field, editObject, itemsLoaded } = this.props;

        if (ids && editObject == null ||
            ids && editObject[thisField] == null ||
            ids && editObject[thisField][field] == null){
            return false;
        }
        return (itemsLoaded && editObject[thisField][field] !== null);
    }

    render() {
        let { items, editObject, field } = this.props,
            obj = items[0],
            thisField = obj[field],
            errs = this.props.errors || {};
        if (!this.isReadyToRender(thisField)) return <Loading />;
        return (
            <div  className="stripe row" onSubmit={this.handleSubmit.bind(this)}>
                <span className='bulk-element field span4'>{thisField || `N/A`}</span>
                <span className={`${h.getInputDivClass(thisField, errs)} bulk-element span5`}>
                    <input name={thisField} className='form-control' type="text"
                        value={editObject[thisField][field]}
                        onChange={this.handleChange.bind(this)}/>

                </span>
                <span className='bulk-element span2'><button className='btn btn-primary'>Submit Bulk Edit</button></span>
            </div>
        );
    }

}

function mapStateToProps(state){
    return {
        editObject: state.endpoint.editObject,
        itemsLoaded: state.endpoint.itemsLoaded,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        dispatch,
    };
}
export default connect(mapStateToProps, mapDispatchToProps)(EndpointBulkForm);
